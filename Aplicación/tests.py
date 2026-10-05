from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from . import views
from .models import (
    Proceso,
    Residuos_pecuarios,
    Residuos_agricolas,
    Rendimientos_agricolas,
    Tipo_rsuo,
)

TEC_RANKINE_CONVENCIONAL = 'Combustión - Ciclo Rankine Convencional accionado con turbina axial'
TEC_RANKINE_ORGANICO = 'Combustión - Ciclo Rankine Orgánico accionado con turbina axial'
TEC_GASIFICACION = TEC_RANKINE_CONVENCIONAL + ' / Gasificación'


class PaginasBasicasTests(TestCase):

    def test_paginas_de_presentacion(self):
        for nombre in ('introduccion', 'inicio', 'funcionamiento', 'fuentes'):
            respuesta = self.client.get(reverse(nombre))
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, 'href="/"')
            self.assertContains(respuesta, 'EMPEZAR PROCESO')
            self.assertContains(respuesta, 'rel="icon"')
            self.assertContains(respuesta, 'Casos posibles')
            self.assertContains(respuesta, 'Procedimiento')
            self.assertContains(respuesta, 'Viabilidad por región')

    def test_iniciar_proceso_crea_un_proceso(self):
        respuesta = self.client.post(reverse('iniciar_proceso'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Proceso.objects.count(), 1)

    def test_boton_reanudar_tras_iniciar_proceso(self):
        respuesta = self.client.post(reverse('iniciar_proceso'))
        proceso_id = int(respuesta.url.rstrip('/').split('/')[-1])
        self.assertEqual(self.client.session['proceso_id'], proceso_id)

        respuesta = self.client.get(reverse('fuentes'))
        self.assertContains(respuesta, 'Reanudar proceso')
        self.assertContains(respuesta, f'/viabilidad/{proceso_id}')

        respuesta = self.client.get(reverse('viabilidad', args=[proceso_id]))
        self.assertEqual(self.client.session['ultima_url'], f'/viabilidad/{proceso_id}')

    def test_boton_reanudar_sin_proceso_vuelve_a_empezar(self):
        respuesta = self.client.post(reverse('iniciar_proceso'))
        proceso_id = int(respuesta.url.rstrip('/').split('/')[-1])
        Proceso.objects.get(id=proceso_id).delete()

        respuesta = self.client.get(reverse('fuentes'))
        self.assertContains(respuesta, 'EMPEZAR PROCESO')
        self.assertNotContains(respuesta, 'Reanudar proceso')


class ViabilidadTests(TestCase):

    def test_pacifica_usa_radio_de_6_km(self):
        viable = Proceso.objects.create()
        self.client.post(reverse('viabilidad', args=[viable.id]), {'region': 'pacifica', 'distancia': 5.9})
        viable.refresh_from_db()
        self.assertEqual(viable.resultado, 'viable')

        inviable = Proceso.objects.create()
        self.client.post(reverse('viabilidad', args=[inviable.id]), {'region': 'pacifica', 'distancia': 7})
        inviable.refresh_from_db()
        self.assertEqual(inviable.resultado, 'inviable')


class FlujoCompletoTests(TestCase):

    def _seleccionar_datos_agricolas(self):
        for rendimiento in Rendimientos_agricolas.objects.filter(region='amazonia'):
            duplicados = Rendimientos_agricolas.objects.filter(
                departamento=rendimiento.departamento, cultivo=rendimiento.cultivo
            ).count()
            if duplicados != 1:
                continue
            for residuo in Residuos_agricolas.objects.filter(cultivo=rendimiento.cultivo):
                pares = Residuos_agricolas.objects.filter(
                    cultivo=residuo.cultivo, residuo=residuo.residuo
                ).count()
                if pares == 1:
                    return rendimiento, residuo
        self.fail('No existe combinacion rendimiento/residuo para la region amazonia')

    def test_flujo_completo_hasta_resultados(self):
        respuesta = self.client.post(reverse('iniciar_proceso'))
        proceso_id = int(respuesta.url.rstrip('/').split('/')[-1])

        respuesta = self.client.post(
            reverse('viabilidad', args=[proceso_id]), {'region': 'amazonia', 'distancia': 5}
        )
        self.assertEqual(respuesta.status_code, 200)

        rendimiento, residuo = self._seleccionar_datos_agricolas()
        respuesta = self.client.post(
            reverse('agricola', args=[proceso_id]),
            {
                'cultivo': residuo.cultivo,
                'residuo': residuo.residuo,
                'hectareas': 10,
                'departamento': rendimiento.departamento,
            },
        )
        self.assertEqual(respuesta.status_code, 302)

        animal = Residuos_pecuarios.objects.first()
        respuesta = self.client.post(
            reverse('pecuaria', args=[proceso_id]),
            {'animal': animal.animal, 'tipo': animal.tipo, 'cantidad': 1000},
        )
        self.assertEqual(respuesta.status_code, 302)

        respuesta = self.client.post(reverse('rsu', args=[proceso_id]), {'masa_RSU': 1000})
        self.assertEqual(respuesta.status_code, 302)

        tipo_rsuo = Tipo_rsuo.objects.first()
        respuesta = self.client.post(
            reverse('rsuo', args=[proceso_id]), {'tipo': tipo_rsuo.tipo, 'masa_RSUO': 500}
        )
        self.assertEqual(respuesta.status_code, 302)

        respuesta = self.client.post(reverse('demanda', args=[proceso_id]), {'cant_hab': 1000})
        self.assertEqual(respuesta.status_code, 302)

        respuesta = self.client.get(reverse('resultados', args=[proceso_id]))
        self.assertEqual(respuesta.status_code, 200)

        proceso = Proceso.objects.get(id=proceso_id)
        self.assertTrue(proceso.Pot_requerida)
        self.assertGreater(proceso.pot_CGD, 0.1)
        self.assertIn(proceso.caso, ['caso1', 'caso2', 'caso3', 'caso4', 'caso5', 'caso6'])
        self.assertTrue(proceso.rt_final)

        if proceso.caso != 'caso4':
            self.assertTrue(proceso.tec_final)
            self.assertGreaterEqual(proceso.cant_plantas, 1)
            self.assertIn(str(proceso.cant_plantas), proceso.comentario)

        comentario_en_respuesta = proceso.comentario
        views.comentario_resultado(proceso)
        proceso.refresh_from_db()
        self.assertEqual(comentario_en_respuesta, proceso.comentario)

        self.assertContains(respuesta, 'Combustión empleando Ciclo rankine orgánico')


class RegresionPunitPequenoTests(TestCase):

    def test_e1f1_con_punit_menor_a_0_1(self):
        proceso = Proceso.objects.create()
        cap, tecnologia = views.PROCESO_E1F1(proceso, 0.05)
        self.assertEqual(cap, [])
        self.assertEqual(tecnologia, 'Ninguna')
        self.assertEqual(proceso.cap_serializado, '[]')

    def test_e2f2_con_punit_menor_a_0_1(self):
        proceso = Proceso.objects.create()
        cap, tecnologia = views.PROCESO_E2F2(proceso, 0.05)
        self.assertEqual(cap, [])
        self.assertEqual(tecnologia, 'Ninguna')
        self.assertEqual(proceso.cap_serializado, '[]')


class ResultadosSinDemandaTests(TestCase):

    def test_resultados_sin_datos_responde_200(self):
        proceso = Proceso.objects.create()
        respuesta = self.client.get(reverse('resultados', args=[proceso.id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'DEBE INGRESAR ALGUNA BIOMASA RESIDUAL')


class PlantillaResultadosTests(TestCase):

    def _render(self, **campos):
        proceso = Proceso.objects.create(caso='caso2', rt_final='Termoquímica', edf=1000)
        for atributo, valor in campos.items():
            setattr(proceso, atributo, valor)
        proceso.save()
        return render_to_string('resultados.html', {'proceso': proceso, 'visual': True})

    def test_seccion_rankine_convencional_se_muestra(self):
        html = self._render(tec_final=TEC_RANKINE_CONVENCIONAL)
        self.assertIn('Combustión empleando Ciclo rankine convencional', html)

    def test_seccion_rankine_organico_no_se_muestra_por_otra_tecnologia(self):
        html = self._render(tec_final=TEC_GASIFICACION, tec_final1=TEC_GASIFICACION)
        self.assertIn('Tecnologías por procesos Termoquímicos', html)
        self.assertNotIn('Combustión empleando Ciclo rankine orgánico', html)

    def test_seccion_rankine_organico_se_muestra_con_su_tecnologia(self):
        html = self._render(tec_final=TEC_RANKINE_ORGANICO)
        self.assertIn('Combustión empleando Ciclo rankine orgánico', html)
