# WasteTOEnergyProject

Aplicación de Diseño de Centros de Generación Distribuida - Biomasa residual ZNI de Colombia

Herramienta web que evalúa la viabilidad, el potencial energético de la biomasa residual
(agrícola, pecuaria, RSU y RSUO), la demanda energética de un centro de consumo y la
ruta tecnológica recomendada (termoquímica o bioquímica) para las Zonas No Interconectadas
de Colombia.

**Sitio en vivo:** https://wastetoenergyproject.onrender.com

## ¿Cómo funciona?

La herramienta acompaña el diseño de un Centro de Generación Distribuida (CGD) en 4 pasos:

1. **Viabilidad** — se elige la región y la distancia (km) desde la biomasa hasta el centro
   de consumo. Es viable si la distancia es menor al radio máximo de la región:
   - Pacífica: **6 km**
   - Amazónica: **7.84 km**
   - Orinoquía: **10.49 km**
2. **Biomasa residual** — ingreso de disponibilidad de residuos (se combinan las fuentes que
   apliquen): agrícola (cultivo/residuo/hectáreas), pecuaria (animal/cantidad), RSU (masa) y
   RSUO (tipo/masa). Con esto se calcula el potencial energético y la cobertura de cada ruta
   tecnológica.
3. **Demanda energética** — número de habitantes del centro de consumo → potencia requerida
   (pot_CGD).
4. **Resultados** — se compara la cobertura de ambas rutas y se entrega: ruta tecnológica
   recomendada, tecnología específica, cantidad de plantas y comentario de recomendación.

Guía visual para usuarios: [¿Cómo funciona?](https://wastetoenergyproject.onrender.com/funcionamiento/)

## Resultados posibles (casos)

| Caso | Condición | Ruta tecnológica recomendada |
|------|-----------|------------------------------|
| caso0 | No se requiere potencia adicional | Ninguna |
| caso1 | Termoquímica y bioquímica cubren el 100% | Bioquímica |
| caso2 | Solo termoquímica cubre el 100% | Termoquímica |
| caso3 | Solo bioquímica cubre el 100% | Bioquímica |
| caso4 | Ninguna sola cubre 100%, pero combinadas superan 50% | Híbrida |
| caso5 | Bioquímica cubre más que termoquímica | Bioquímica |
| caso6 | Termoquímica cubre más que bioquímica | Termoquímica |
| caso7 | Ninguna ruta alcanza cobertura suficiente | Ninguna |

Definido en `Aplicación/views.py` (`def_caso`).

## Tests

```bash
python manage.py test
```

Suite actual (10 tests) en `Aplicación/tests.py`:

| Test | Qué verifica | Por qué importa |
|------|--------------|-----------------|
| `test_paginas_de_presentacion` | Introducción, Inicio, ¿Cómo funciona? y Fuentes responden 200 | Las páginas siempre deben renderizar (incluye las nuevas) |
| `test_iniciar_proceso_crea_un_proceso` | "Empezar proceso" crea un Proceso y redirige (302) | Punto de entrada del flujo |
| `test_pacifica_usa_radio_de_6_km` | Pacífica: 5.9 km → viable, 7 km → inviable | Regresión del radio corregido de la región Pacífica (6 km) |
| `test_flujo_completo_hasta_resultados` | Flujo completo: proceso → viabilidad → agrícola → pecuaria → RSU → RSUO → demanda → resultados | Integridad de todo el flujo y que el comentario se genera una sola vez |
| `test_e1f1_con_punit_menor_a_0_1` | `PROCESO_E1F1` con punit < 0.1 no falla y devuelve "Ninguna" | Regresión del `NameError` por división con punit pequeño |
| `test_e2f2_con_punit_menor_a_0_1` | `PROCESO_E2F2` con punit < 0.1 no falla | Igual que el anterior para el escenario E2F2 |
| `test_resultados_sin_datos_responde_200` | Resultados sin datos muestra aviso y responde 200 | Navegación directa a resultados no debe romper |
| `test_seccion_rankine_convencional_se_muestra` | La sección de Rankine convencional aparece cuando es la tecnología final | Regresión de plantilla (`tec_finaL` → `tec_final`) |
| `test_seccion_rankine_organico_no_se_muestra_por_otra_tecnologia` | Con gasificación no aparece la sección de Rankine orgánico | Regresión de la condición mal escrita de Rankine orgánico |
| `test_seccion_rankine_organico_se_muestra_con_su_tecnologia` | Con Rankine orgánico sí aparece su sección | Cobertura de la lógica de mostrado por tecnología |

## Estructura del proyecto

```
BiomasaProject/
├── Aplicación/          # Vistas, modelos, formularios, cálculos y tests
│   ├── views.py         # Lógica del flujo (viabilidad, biomasa, demanda, resultados)
│   ├── models.py        # Modelo Proceso y catálogos de residuos
│   ├── tests.py         # Suite de 10 tests
│   └── migrations/      # Migraciones (la 0002 carga los CSV de fixtures)
├── Biomasa/             # Proyecto Django (settings, urls, wsgi)
├── fixtures/            # Bases de datos CSV de biomasa residual
├── templates/           # Páginas HTML (introducción, proceso, resultados, fuentes…)
├── static/css/          # Estilos
├── requirements.txt     # Dependencias (Django 5.2 LTS, gunicorn, whitenoise)
└── .python-version      # Fija Python 3.11
```

## Requisitos

- Python 3.11

## Ejecutar localmente

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

## Despliegue en Render

Repositorio: https://github.com/CarolPinerosTrujillo/WasteTOEnergyProject

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start command: `python manage.py migrate --noinput && gunicorn Biomasa.wsgi:application --bind 0.0.0.0:$PORT`
- Variables de entorno: `DEBUG=False`, `SECRET_KEY` (generada), `ALLOWED_HOSTS=.onrender.com`
- El archivo `.python-version` fija Python 3.11.

Cada `push` a `main` publica los cambios automáticamente.
Un workflow de GitHub Actions (`.github/workflows/keep-alive.yml`) hace ping cada 10 minutos
para que el sitio no se duerma en el plan gratuito.

## Fuentes y bibliografía

- **Trabajo de grado (origen del proyecto):** PIÑEROS TRUJILLO, Carol. *Algoritmo para apoyar
  el diseño de centros de generación distribuida a partir de biomasa residual en ZNI de
  Colombia.* Trabajo de grado — Ingeniería Mecánica, Universidad Distrital Francisco José de
  Caldas, 2023. Director: Germán Arturo López Martínez.
  https://repository.udistrital.edu.co/items/08f20def-e6c7-4e5c-b383-f985891db842
  (URI: http://hdl.handle.net/11349/39704)
- **Libro de referencia:** BURITICÁ-ARBOLEDA, C. I. et al. (2020). *Los recursos distribuidos
  de bioenergía en Colombia.* Universidad Distrital Francisco José de Caldas. ISBN
  978-958-787-258-3. CC BY-NC-ND 4.0.
  https://libros.udistrital.edu.co/index.php/invest/catalog/book/61
- Listado completo y enlaces complementarios en el sitio:
  [Fuentes y Bibliografía](https://wastetoenergyproject.onrender.com/fuentes/)

## Colaboraciones

¡Las colaboraciones son bienvenidas! El proyecto está abierto a aportes de la comunidad:

1. Haz un *fork* del repositorio.
2. Crea una rama para tu cambio (`git checkout -b mi-mejora`).
3. Ejecuta los tests antes de enviar: `python manage.py test` (deben quedar todos en verde).
4. Abre un *Pull Request* describiendo qué cambia y por qué.

Si encuentras un error o tienes una sugerencia, abre un *issue* en
https://github.com/CarolPinerosTrujillo/WasteTOEnergyProject

## Licencia

Este proyecto se distribuye bajo la licencia **GNU General Public License v3.0** — ver el
archivo [LICENSE](LICENSE). Puedes usar, modificar y redistribuir el código bajo sus
términos (las obras derivadas deben publicarse también con GPL-3.0).
