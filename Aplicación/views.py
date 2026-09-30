import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import *
from .models import *

# Creacion de funcion para vista de home


def introduccion(request):
    context = {}
    return render(request, "introduccion.html", context)


def inicio(request):
    context = {}
    return render(request, "inicio.html", context)


def iniciar_proceso(request):
    proceso = Proceso.objects.create()
    return redirect('viabilidad', proceso.id)


def viabilidad(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        form = ViabilidadForm(request.POST, instance=proceso)
        if form.is_valid():
            form = form.save()
            # Leer R_max de la region
            if form.region == 'amazonia':
                r_max = 7.84
            elif form.region == 'orinoquia':
                r_max = 10.49
            else:
                r_max = 6
            # Sabemos si es viable o no
            if form.distancia >= r_max:
                proceso.resultado = 'inviable'
            else:
                proceso.resultado = 'viable'
            # Guardamos los resultados
            proceso.save()
    else:
        form = ViabilidadForm()

    context = {
        'proceso': proceso,
        'form': form,
    }
    return render(request, "viabilidad.html", context)


def agricola_pregunta(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        if respuesta == 'True':
            proceso.agricola = True
            proceso.save()
            return redirect('agricola', proceso_id)
        else:
            return redirect('pecuaria', proceso_id)
    else:
        messages.error(request, 'No hay respuesta')
        return redirect('agricola', proceso_id)


def agricola(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        form = ResiduosAgricolasForm(request.POST, proceso=proceso)
        if form.is_valid():
            cultivo = form.cleaned_data['cultivo']
            residuo = form.cleaned_data['residuo']
            hectareas = form.cleaned_data['hectareas']
            departamento = form.cleaned_data['departamento']

            residuo_agricola = Residuos_agricolas.objects.get(
                cultivo=cultivo, residuo=residuo)
            fr = residuo_agricola.fr
            ybas = residuo_agricola.ybas
            dr = residuo_agricola.dr
            pci = residuo_agricola.pci
            pb = residuo_agricola.pb
            wf = residuo_agricola.wf

            ac = hectareas

            rendimiento_agricola = Rendimientos_agricolas.objects.get(
                departamento=departamento, cultivo=cultivo)
            rc = rendimiento_agricola.rc

            # Calculo de masa de residuo
            masa_agricola = ac*rc*fr*dr

            #SE DEFINE QUE EL POTENCIAL DE BIOMASA AGRICOLA SE DEFINE POR LA CANTIDAD DE HUMEDAD QUE TIENE, 
            # SI LA HUMEDAD ES MENOR A 0.5 SE DETERMINA POT TERMOQUIMICO, SI ES MAYOR A 0.5 POTENCIAL POR RUTA BIOQUIMICA
            if wf<0.5:
                # Calculo potencial energia por RT termoquimica
                pot_rt_termo_agri = (masa_agricola*ybas*pci)/3600
                pot_rt_bioq_agri = 0
            else:
                # Calculo potencial energético por RT Bioquimica
                pciMetano = 21600
                pot_rt_bioq_agri = (masa_agricola*pb*pciMetano)/3600
                pot_rt_termo_agri = 0


            # Guardar Datos Biomasa Agricola
            biomasa_agricola = Biomasa_agricola.objects.create(
                residuo_agricola=residuo_agricola,
                hectareas=hectareas,
                rendimiento_agricola=rendimiento_agricola,
                masa_agricola=masa_agricola,
                pot_rt_termo_agri=pot_rt_termo_agri,
                pot_rt_bioq_agri=pot_rt_bioq_agri
            )
            biomasa_agricola.save()

            # Calculo de masa agricola humeda o seca

            if wf > 0.5:
                proceso.masa_agricola_humeda += masa_agricola
                proceso.biomasa_humeda += masa_agricola
            else:
                proceso.masa_agricola_seca += masa_agricola
                proceso.biomasa_seca += masa_agricola

            proceso.biomasa_agricola.add(biomasa_agricola)
            proceso.total_hectareas += hectareas
            proceso.total_masa_agricola += masa_agricola
            proceso.total_pot_rt_termo_agri += pot_rt_termo_agri
            proceso.total_pot_rt_bioq_agri += pot_rt_bioq_agri
            
            proceso.save()

            return redirect('agricola', proceso_id)

    else:
        form = ResiduosAgricolasForm(proceso=proceso)

    context = {
        'proceso': proceso,
        'form': form,
    }
    return render(request, "agricola.html", context)


def pecuaria_pregunta(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        if respuesta == 'True':
            proceso.pecuaria = True
            proceso.save()
            return redirect('pecuaria', proceso_id)
        else:
            return redirect('rsu', proceso_id)
    else:
        messages.error(request, 'No hay respuesta')
        return redirect('pecuaria', proceso_id)


def pecuaria(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        form = ResiduosPecuariosForm(request.POST)
        if form.is_valid():
            animal = form.cleaned_data['animal']
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']

            residuo_pecuario = Residuos_pecuarios.objects.get(
                animal=animal, tipo=tipo)
            pb = residuo_pecuario.pb
            pe = residuo_pecuario.pe
            dr = residuo_pecuario.dr

            cant_animal = cantidad

            # Calculo de masa de residuo
            masa_pecuaria = (cant_animal*pe*dr*365)/1000

            # Calculo potencial energético por RT Bioquimica
            pciMetano = 21600
            pot_rt_bioq_pecu = (masa_pecuaria*pb*pciMetano)/3600

            # Guardar Datos Biomasa Pecuaria
            biomasa_pecuaria = Biomasa_pecuaria.objects.create(
                residuo_pecuario=residuo_pecuario,
                cantidad=cantidad,
                masa_pecuaria=masa_pecuaria,
                pot_rt_bioq_pecu=pot_rt_bioq_pecu
            )
            biomasa_pecuaria.save()

            proceso.biomasa_humeda += masa_pecuaria
            proceso.biomasa_pecuaria.add(biomasa_pecuaria)
            proceso.total_cantidad += cantidad
            proceso.total_masa_pecuaria += masa_pecuaria
            proceso.total_pot_rt_bioq_pecu += pot_rt_bioq_pecu
            proceso.save()

            return redirect('pecuaria', proceso_id)

    else:
        form = ResiduosPecuariosForm()

    context = {
        'proceso': proceso,
        'form': form,
    }
    return render(request, "pecuaria.html", context)


def rsu_pregunta(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        print(respuesta)
        if respuesta == 'True':
            proceso.rsu = True
            proceso.save()
            return redirect('rsu', proceso_id)
        else:
            return redirect('rsuo', proceso_id)
    else:
        print("Depurador: ejecicion no valido")
        return redirect('rsu', proceso_id)


def rsu(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        form1 = CantidadRSUForm(request.POST)
        form2 = ResiduosRSUForm(request.POST)
        if form1.is_valid():
            cant_personas = form1.cleaned_data['cant_personas']
            region = form1.cleaned_data['region']

            produccion_rsu = Produccion_rsu.objects.get(region=region)
            pro_RSU_hab = produccion_rsu.pro_RSU_hab
            dr = produccion_rsu.dr
            masa_RSU = (cant_personas*dr*pro_RSU_hab*365)/1000

            biomasa_rsu = Biomasa_rsu.objects.create(
                produccion_rsu=produccion_rsu,
                cant_personas=cant_personas,
                masa_RSU=masa_RSU,
            )

        elif form2.is_valid():
            masa_RSU = form2.cleaned_data['masa_RSU']

            biomasa_rsu = Biomasa_rsu.objects.create(
                masa_RSU=masa_RSU,
            )

        else:
            masa_RSU = None

        if masa_RSU is not None:
            PCI_prom_RSU = 20871.72    #PCI promedio de los RSU secos
            pot_rt_termo_rsu = (PCI_prom_RSU*masa_RSU*0.582)/3600

            biomasa_rsu.pot_rt_termo_rsu = pot_rt_termo_rsu
            biomasa_rsu.save()

            proceso.biomasa_seca += masa_RSU
            proceso.biomasa_rsu.add(biomasa_rsu)
            proceso.total_masa_rsu += masa_RSU
            proceso.total_pot_rt_termo_rsu += pot_rt_termo_rsu
            proceso.save()

        return redirect('rsu', proceso_id)
    else:
        form1 = CantidadRSUForm()
        form2 = ResiduosRSUForm()

    context = {
        'proceso': proceso,
        'form1': form1,
        'form2': form2,
    }
    return render(request, "rsu.html", context)


def rsuo_pregunta(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        if respuesta == 'True':
            proceso.rsuo = True
            proceso.save()
            return redirect('rsuo', proceso_id)
        else:
            return redirect('demanda', proceso_id)
    else:
        messages.error(request, 'No hay respuesta')
        return redirect('rsu', proceso_id)


def rsuo(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        form = ResiduosRSUOForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            masa_RSUO = form.cleaned_data['masa_RSUO']

            tipo_rsuo = Tipo_rsuo.objects.get(tipo=tipo)
            pb = tipo_rsuo.pb
            dr = tipo_rsuo.dr

            PCImetano = 21600
            pot_rt_bioq_rsuo = (pb*dr*PCImetano*masa_RSUO)/3600

            biomasa_rsuo = Biomasa_rsuo.objects.create(
                tipo_rsuo=tipo_rsuo,
                masa_RSUO=masa_RSUO,
                pot_rt_bioq_rsuo=pot_rt_bioq_rsuo,
            )

            proceso.biomasa_humeda += masa_RSUO
            proceso.biomasa_rsuo.add(biomasa_rsuo)
            proceso.total_masa_rsuo += masa_RSUO
            proceso.total_pot_rt_bioq_rsuo += pot_rt_bioq_rsuo
            proceso.save()

            return redirect('rsuo', proceso_id)
        else:
            print("Depurador: ejecicion no valido")
    else:
        form = ResiduosRSUOForm()

    context = {
        'proceso': proceso,
        'form': form,
    }
    return render(request, "rsuo.html", context)


def demanda(request, proceso_id):
    proceso = Proceso.objects.get(id=proceso_id)
    if request.method == 'POST':
        form1 = CantidadDemandaForm(request.POST)
        form2 = DemandaForm(request.POST)
        if form1.is_valid():
            cant_hab = form1.cleaned_data['cant_hab']
            consumo_per_capital = (1492.5)/1000.0
            
            ed = round(cant_hab * consumo_per_capital, 5)
        elif form2.is_valid():
            ed = form2.cleaned_data['ed']
        else:
            ed = None

        if ed is not None:
            tasa_crecimiento = 0.0181   
            edf = round(ed *((1+tasa_crecimiento)**20),5)
            pot_CGD = round((edf/365) / (24*0.6), 5)

            if pot_CGD >= 0.1:
                proceso.Pot_requerida = True
            else:
                proceso.Pot_requerida = False

            proceso.ed = ed
            proceso.edf = edf
            proceso.pot_CGD = pot_CGD

            

            if pot_CGD < 0.1:
                    proceso.comentario_demanda = (f' La potencia global de la planta es {proceso.pot_CGD} MW. Se tiene estimado para este programa que la potencia mínima para proyectar una planta de generación de electricidad con biomasa residual es de 0,1 MW. La potencia de planta requerida para el centro de consumo no supera el valor mínimo. ')   
            else:
                    proceso.comentario_demanda = (f'Las potencias requeridas, global de la planta es {proceso.pot_CGD} MW. La demanda enérgetica del usuario es apta para proyectar una central de generación distribuida con Biomasa residual u otras energías alternativas. La potencia mínima para proyectar una planta de generación de electricidad con biomasa residual es mínimo de 0,1 MW, de acuerdo a las capacidades actuales de tecnologías de transformacíon.')

            proceso.save()



        return redirect('demanda', proceso_id)
    else:
        form1 = CantidadDemandaForm()
        form2 = DemandaForm()

    context = {
        'proceso': proceso,
        'form1': form1,
        'form2': form2,
    }
    return render(request, "demanda.html", context)


  
def Viabilidad_RT(proceso):   #PROCESO D1 - D2
    #PROCESO D1 - D2
    # PROCESO D1 - RUTA TERMOQUIMICA
    pot_teo_termo = proceso.total_pot_rt_termo_agri + proceso.total_pot_rt_termo_rsu
    pot_teo_termo_unit = pot_teo_termo/(8760*0.6)

    proceso.pot_teo_termo = pot_teo_termo
    proceso.pot_teo_termo_unit = pot_teo_termo_unit

    if pot_teo_termo_unit > 3:
        eficiencia = 0.26
    else:
        eficiencia = 0.22

    pot_tec_termo = pot_teo_termo*eficiencia
    pot_tec_termo_planta = round(pot_teo_termo_unit*eficiencia,5)

    proceso.pot_tec_termo_planta = pot_tec_termo_planta
    proceso.pot_tec_termo = pot_tec_termo

    cub_rt_termo = round((pot_tec_termo/proceso.edf)*100  ,5) if proceso.edf else 0.0
    proceso.cub_rt_termo = cub_rt_termo

    if proceso.cub_rt_termo>=100 and proceso.pot_tec_termo_planta>=0.1:
        proceso.cub_termo100 = True
    else:
        if proceso.pot_tec_termo_planta>=0.1:
            proceso.Termoquimica=True
        else:
            proceso.Termoquimica=False



    proceso.save()


    #PROCESO D2 - RT BIOQUMICA
    pot_teo_bioq = proceso.total_pot_rt_bioq_agri + proceso.total_pot_rt_bioq_pecu + proceso.total_pot_rt_bioq_rsuo
    pot_teo_bioq_unit = pot_teo_bioq/(8760*0.6)

    proceso.pot_teo_bioq = pot_teo_bioq
    proceso.pot_teo_bioq_unit = pot_teo_bioq_unit

    if pot_teo_bioq_unit > 3:
        eficiencia = 0.26
    else:
        eficiencia = 0.22

    pot_tec_bioq = pot_teo_bioq*eficiencia
    pot_tec_bioq_planta = round(pot_teo_bioq_unit*eficiencia, 5)

    proceso.pot_tec_bioq_planta = pot_tec_bioq_planta
    proceso.pot_tec_bioq = pot_tec_bioq

    cub_rt_bioq = (pot_tec_bioq/proceso.edf)*100 if proceso.edf else 0.0
    cub_rt_bioq = round(cub_rt_bioq, 5)

    proceso.cub_rt_bioq = cub_rt_bioq

    if proceso.cub_rt_bioq>=100 and proceso.pot_tec_bioq_planta>=0.1:
        proceso.cub_bioq100 = True
    else:
        proceso.cub_bioq100 = False
        if proceso.pot_tec_bioq_planta>=0.1:
            proceso.Bioquimica=True
        else:
            proceso.Bioquimica=False
    
    proceso.save()
    
    


    #Validar EVAL_RT_HIBRIDA
    proceso.Pot_CGD_parcial_bioq = (proceso.cub_rt_bioq / 100)*proceso.pot_CGD
    proceso.Pot_CGD_parcial_termo= (proceso.cub_rt_termo / 100)*proceso.pot_CGD
    if proceso.cub_rt_termo >=50 or proceso.cub_rt_bioq>=50:
        proceso.Hibrida = False
    else:
        proceso.cub_total =  proceso.cub_rt_termo + proceso.cub_rt_bioq 
        if proceso.Pot_CGD_parcial_termo >=0.1 and proceso.Pot_CGD_parcial_bioq >=0.1 and proceso.Bioquimica==True and proceso.Termoquimica==True and proceso.cub_total>=50:
            proceso.Hibrida = True       
        else:
            proceso.Hibrida = False

    proceso.save()



def def_caso(proceso):
    Viabilidad_RT(proceso)

    
    if proceso.Pot_requerida == False:
        proceso.caso='caso0'
        proceso.rt_final='Ninguna'
    elif proceso.cub_termo100 == True and proceso.cub_bioq100 == True:
        proceso.caso='caso1'
        proceso.rt_final = 'Bioquímica'
    elif proceso.cub_termo100 == True:
        proceso.caso='caso2'
        proceso.rt_final = 'Termoquímica'
    elif proceso.cub_bioq100 == True:
        proceso.caso='caso3'
        proceso.rt_final = 'Bioquímica'
    elif proceso.Hibrida == True:
        proceso.caso='caso4'
        proceso.rt_final = 'Hibrida'
        
    elif proceso.cub_rt_bioq >= proceso.cub_rt_termo and proceso.Bioquimica == True:
        proceso.caso='caso5'
        proceso.rt_final = 'Bioquímica'
   
    elif proceso.cub_rt_termo >= proceso.cub_rt_bioq  and proceso.Termoquimica == True:
        proceso.caso='caso6'
        proceso.rt_final = 'Termoquímica'

    else:
        proceso.caso='caso7'
        proceso.rt_final = 'Ninguna'
   
    
    proceso.save()








def PROCESO_E1F1(proceso, punit): #RUTA TERMOQUIMICA
    cap = []
    proceso.tec_final = 'Ninguna'

    if punit >= 10:
        proceso.tec_final = 'Combustión - Ciclo Rankine Convencional accionado con turbina axial / Gasificación'
        proceso.tipo1 = True
        proceso.tipo2 = True
        cap =[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]


    elif punit >= 1:
        proceso.tec_final = 'Combustión - Ciclo Rankine Convencional accionado con turbina axial'
        proceso.tipo1 = True
        cap = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]


    elif punit >= 0.1:
        proceso.tec_final = 'Combustión - Ciclo Rankine Orgánico accionado con turbina axial'
        proceso.tipo1 = True
        cap=[0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]    
    else:
        proceso.tec_final = 'Ninguna'
    
    # Serializar y almacenar la lista cap
    cap_serializado = json.dumps(cap)
    proceso.cap_serializado = cap_serializado

    proceso.save()

    # Deserializar la lista cap para usarla en otra función
    proceso.cap = cap

    proceso.save()
    return cap, proceso.tec_final
    
    
def PROCESO_E2F2(proceso, punit): #RUTA BIOQUIMICA
    cap = []
    proceso.tec_final = 'Ninguna'

    if punit >= 0.1:
        proceso.tec_final = 'Digestión anaerobia - generación de biogas - impulsor MCI'
        proceso.tipo3 = True
        cap=[0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]

    # Serializar y almacenar la lista cap
    proceso.cap_serializado = json.dumps(cap)

    proceso.save()
    return cap, proceso.tec_final


def capacidad_y_cantidad_plantasFP(proceso, cap, punit):
    #PROCESO FP
    for i in cap:
        #if i>=punit:
        if punit/i >=1 :       
            if (proceso.pot_CGD/i)-int(proceso.pot_CGD/i) <0.5:
                Cant_plantas_1=int(proceso.pot_CGD/i)                     
            else:
                Cant_plantas_1=int(proceso.pot_CGD/i) +1   

            MW_ofrecido=Cant_plantas_1*i
            MW_faltante = round(MW_ofrecido-proceso.pot_CGD,3)


            if MW_faltante <=-0.001:
                proceso.comentario_cubrimiento_planta= (f'Cubre total de demanda energética. ')
                proceso.cant_plantas=Cant_plantas_1+1
                proceso.cap_planta=i 
                
            else:
                proceso.comentario_cubrimiento_planta= (f'Cubre total de demanda energética')
                proceso.cant_plantas=Cant_plantas_1
                proceso.cap_planta=i
                #proceso.comentario_cantplantas= (f'No plantas: {proceso.cant_plantas} Potencia:{cap_planta} MW')
                #x=(pot_CGD/i)-int(pot_CGD/i) 
                #print(comentario_cantplantas) 
                #print(comentario_cubrimiento_planta)
                #print(punit)
                #print(pot_CGD)
                break
        else:
            pass

    proceso.save()
    return proceso.cap_planta, proceso.cant_plantas, proceso.comentario_cantplantas, proceso.comentario_cubrimiento_planta  

def capacidad_y_cantidad_plantasFP2(proceso, cap, punit):
    #proceso.Pot_CGD_parcial_bioq
    #PROCESO FP2 - RUTA BIOQUIMICA

    for i in cap:
        #if i>=punit:
        if punit/i >=1 :     

            if (proceso.Pot_CGD_parcial_bioq/i)-int(proceso.Pot_CGD_parcial_bioq/i) <0.5:
                Cant_plantas_1=int(proceso.Pot_CGD_parcial_bioq/i)                     
            else:
                Cant_plantas_1=int(proceso.Pot_CGD_parcial_bioq/i) +1   

            MW_ofrecido=Cant_plantas_1*i
            MW_faltante = round(MW_ofrecido-proceso.Pot_CGD_parcial_bioq,3)

            
            if MW_faltante <=-0.001:
                proceso.comentario_cubrimiento_planta= (f'Cubre el total de demanda energética,pero debe complementar con más biomasa residual para procesos bioqumicos, de lo contrario seleccione una potencia de planta inferior según capacidades disponibles comercialmente.')
                proceso.cant_plantas=Cant_plantas_1+1
                proceso.cap_planta=i 


                
            else:
               
                proceso.comentario_cubrimiento_planta= (f'Cubre total de demanda energética con la biomasa disponible')
                proceso.cant_plantas=Cant_plantas_1
                proceso.cap_planta=i
                #proceso.comentario_cantplantas= (f'No plantas: {proceso.cant_plantas} Potencia:{proceso.cap_planta} MW')
                #x=(pot_CGD/i)-int(pot_CGD/i) 
                #print(comentario_cantplantas) 
                #print(comentario_cubrimiento_planta)
                #print(punit)
                #print(pot_CGD)
                break  
        else:
            pass

    proceso.save()  
    return proceso.cap_planta, proceso.cant_plantas, proceso.comentario_cantplantas, proceso.comentario_cubrimiento_planta    


def capacidad_y_cantidad_plantasFP3(proceso, cap, punit):
    #PROCESO FP3 - RUTA TERMOQUIMICA
    #Pot_CGD_parcial_termo
    for i in cap:
        #if i>=punit:
        if punit/i >=1 :    



            if (proceso.Pot_CGD_parcial_termo/i)-int(proceso.Pot_CGD_parcial_termo/i) <0.5:
                Cant_plantas_1=int(proceso.Pot_CGD_parcial_termo/i)                     
            else:
                Cant_plantas_1=int(proceso.Pot_CGD_parcial_termo/i) +1   

            MW_ofrecido=Cant_plantas_1*i
            MW_faltante = round(MW_ofrecido-proceso.Pot_CGD_parcial_termo,3)


            if MW_faltante <=-0.001:
                proceso.comentario_cubrimiento_planta= (f'Cubre el total de demanda energética,pero debe complementar con mas biomasa residual para procesos termoquímicos, de lo contrario seleccione una potencia de planta inferior según capacidades disponibles comercialmente.')
                proceso.cant_plantas=Cant_plantas_1+1
                proceso.cap_planta=i 
                
            else:
                proceso.comentario_cubrimiento_planta= (f'Cubre total de demanda energética con la biomasa disponible')
                proceso.cant_plantas=Cant_plantas_1
                proceso.cap_planta=i
                #proceso.comentario_cantplantas= (f'No plantas: {cant_plantas} Potencia:{cap_planta} MW')
                #x=(pot_CGD/i)-int(pot_CGD/i) 
                #print(comentario_cantplantas) 
                #print(comentario_cubrimiento_planta)
                #print(punit)
                #print(pot_CGD)
                break  
        else:
            pass
        
    proceso.save()  
    return proceso.cap_planta, proceso.cant_plantas, proceso.comentario_cantplantas, proceso.comentario_cubrimiento_planta    


def calculo_costos(proceso):
     # Estimacion de costos
     #TIPO1 =
    if proceso.tipo1:
        #Termica a biomasa
        KW_total= proceso.cap_planta*proceso.cant_plantas*1000
        ref_unitario= KW_total*3758   #US$/KW
        CVNC=float(proceso.cap_planta*proceso.cant_plantas* 8760 * 5.6 ) #US$/año
        
        proceso.capex1=float(ref_unitario)   #US$  Dolares
        proceso.opex1=proceso.capex1*0.02 +CVNC #US$/año

        #proceso.capex1 = 2706378 * (proceso.masa_agricola_seca + proceso.total_masa_rsu)
        #proceso.opex1 = 513922 * (proceso.masa_agricola_seca+ proceso.total_masa_rsu)

    if proceso.tipo2:
        # Costos estimados de gasificación
        proceso.capex2 = 5060471 * (proceso.masa_agricola_seca + proceso.total_masa_rsu)
        proceso.opex2 = 2615198 * (proceso.masa_agricola_seca + proceso.total_masa_rsu)

    if proceso.tipo3:
        #termica a Biogas
        KW_total= proceso.cap_planta*proceso.cant_plantas*1000
        ref_unitario= KW_total*1341  #US$/KW
        CVNC=float(proceso.cap_planta*proceso.cant_plantas* 8760 * 9.3 ) #US$/año
        
        proceso.capex3=float(ref_unitario)   #US$  Dolares
        proceso.opex3=proceso.capex3*0.02 +CVNC #US$/año

        #proceso.capex3 = 857917 *(proceso.total_masa_pecuaria + proceso.total_masa_rsuo+proceso.masa_agricola_humeda)
        #proceso.opex3 = 215515 * (proceso.total_masa_pecuaria + proceso.total_masa_rsuo+proceso.masa_agricola_humeda)   


def comentario_resultado(proceso):

    if proceso.caso=='caso0':
        proceso.comentario = (
                f'No hay demanda energética suficiente para proyectar una CGD con la biomasa disponible, la potencia minima requerida es de 0,1 MW, y se esta requiriendo {round(proceso.pot_CGD,2)} MW para el centro de consumo. En ese caso lo recomendado es optar por un proceso diferente de valorización de la biomasa residual, por ejemplo, compostaje.')

    if proceso.caso=='caso1':
        proceso.comentario = (
                f'Las dos rutas tecnológicas cubren el 100% la demanda energética con la biomasa disponible. La ruta técnológica seleccionada es {proceso.rt_final}, se considera la ruta con menores costos asociados a inversión, operación y mantenimiento. La potencia de planta obtenida de la biomasa residual fue {round(proceso.pot_tec_bioq_planta,2)} MW y potencia global de planta requerida es de {round(proceso.pot_CGD,2)} MW. Se determinó como tecnología recomendada {proceso.tec_final}, y para cubrir la demanda energética del centro de consumo se determino cantidad de {proceso.cant_plantas} plantas (unidades) , cada una con potencia de {proceso.cap_planta} MW')

    if proceso.caso=='caso2':
        proceso.comentario = (
                f'Si es posible cubrir el 100% de la demanda energética con la biomasa disponible. La ruta técnológica es {proceso.rt_final}. La potencia de planta obtenida de la biomasa residual fue {round(proceso.pot_tec_termo_planta,2)} MW y la planta requerida es de {round(proceso.pot_CGD,2)} MW. Se determinó como tecnología recomendada {proceso.tec_final}, y para cubrir la demanda energética del centro de consumo se determino cantidad de {proceso.cant_plantas} plantas (unidades) , cada una con potencia de {proceso.cap_planta} MW')

    if proceso.caso=='caso3':
        proceso.comentario = (
                f'Si es posible cubrir el 100% de la demanda energética con la biomasa disponible. La ruta técnológica es {proceso.rt_final}. La potencia de planta obtenida de la biomasa residual fue {round(proceso.pot_tec_bioq_planta,2)} MW y la planta requerida es de {round(proceso.pot_CGD,2)} MW. Se determinó como tecnología recomendada {proceso.tec_final}, y para cubrir la demanda energética del centro de consumo se determino cantidad de {proceso.cant_plantas} plantas (unidades) , cada una con potencia de {proceso.cap_planta} MW')
    
    if proceso.caso=='caso4': 
        proceso.comentario = (f'Se logra un cubrimiento de {round(proceso.cub_total,2)}% de la demanda con las dos rutas técnológicas. La potencia de planta obtenida de la biomasa residual fue {round(proceso.pot_tec_bioq_planta,2)} MW para ruta Bioquimica, y {round(proceso.pot_tec_termo_planta,2)} MW para ruta termoquímica. Se dan los resultados de tecnología recomendada para ruta técnológica. Si el cubrimiento energético se considera insuficiente, se recomienda reunir más recursos de biomasa residual para lograr un mayor potencial energético (Iniciar nuevo proceso) y obtener un mayor cubrimiento energético. ') 

    
    if proceso.caso=='caso5': 
        proceso.comentario = (
            f'No es posible cubrir el 100% de la demanda con la biomasa disponible. Se logra cubrir parcialmente {proceso.cub_rt_bioq}% con la ruta Bioquimica, el faltante se debe cubrir con otra fuente distinta a la Biomasa residual ingresada u otra fuente de generación electrica. La potencia de planta obtenida de la biomasa residual fue {round(proceso.pot_tec_bioq_planta,2)} MW. La tecnología recomendada es {proceso.tec_final}, cantidad de {proceso.cant_plantas} con una capacidad de planta de {proceso.cap_planta} MW cada una. Si el cubrimiento energético se considera insuficiente, se recomienda reunir más recursos de biomasa residual para lograr un mayor potencial energético (Iniciar nuevo proceso) y obtener un mayor cubrimiento energético. ')  

    if proceso.caso=='caso6': 
        proceso.comentario = (
            f'No es posible cubrir el 100% de la demanda con la biomasa disponible. Se logra cubrir parcialmente {proceso.cub_rt_termo}% con la ruta Termoquímica, el faltante se debe cubrir con otra fuente distinta a la Biomasa residual ingresada u otra fuente de generación electrica. La potencia de planta obtenida de la biomasa residual fue {round(proceso.pot_tec_termo_planta,2)} MW y la planta requerida es de {round(proceso.pot_CGD,2)} MW. La tecnología recomendada es {proceso.tec_final}, cantidad de {proceso.cant_plantas} con una capacidad de planta de {proceso.cap_planta} MW cada una. Si el cubrimiento energético se considera insuficiente, se recomienda reunir más recursos de biomasa residual para lograr un mayor potencial energético (Iniciar nuevo proceso) y obtener un mayor cubrimiento energético. ')  
    if proceso.caso=='caso7':
        proceso.comentario = (
            f'Existe un demanda energética mayor a 0,1 MW (Suficiente), sin embargo ninguna ruta técnológica fue seleccionada, la biomasa disponible se considera muy poca o de bajo potencial energético para emplear tecnologías de generación de electricidad. En ese caso lo recomendado es optar por un proceso diferente de valorización de la biomasa residual, por ejemplo, compostaje.')

    proceso.save()


def resultados(request,proceso_id): #RESULTADOS DEF_PUNIT
    proceso = Proceso.objects.get(id=proceso_id)
    def_caso(proceso)

    suma_termo = proceso.total_pot_rt_termo_agri + proceso.total_pot_rt_termo_rsu
    suma_bioq = proceso.total_pot_rt_bioq_agri + proceso.total_pot_rt_bioq_pecu + proceso.total_pot_rt_bioq_rsuo
    proceso.suma_termo = suma_termo
    proceso.suma_bioq = suma_bioq

    if proceso.suma_termo >0  or proceso.suma_bioq > 0 or proceso.edf >0:
        visual=True


        if proceso.caso=='caso1':
            if proceso.pot_CGD>=0.2:
                punit=proceso.pot_CGD/2

            else:
                punit=proceso.pot_CGD
            
            proceso.punit = punit
            cap, proceso.tec_final = PROCESO_E2F2(proceso, punit)
            capacidad_y_cantidad_plantasFP(proceso  , cap , punit)

        if proceso.caso=='caso2':
            if proceso.pot_CGD>=0.2:
                punit=proceso.pot_CGD/2

            else:
                punit=proceso.pot_CGD
            proceso.punit = punit
            cap, proceso.tec_final = PROCESO_E1F1(proceso, punit) #RT Termoquimica - obtener tec final y cap 
            capacidad_y_cantidad_plantasFP(proceso  , cap , punit)

        if proceso.caso=='caso3':
            if proceso.pot_CGD>=0.2:
                punit=proceso.pot_CGD/2
            else:
                punit=proceso.pot_CGD
            proceso.punit = punit
            cap, proceso.tec_final = PROCESO_E2F2(proceso, punit)
            capacidad_y_cantidad_plantasFP(proceso  , cap , punit)
        


        if proceso.caso=='caso4': #RT HIBRIDA   
            if proceso.pot_tec_bioq_planta>=0.2:
                punit=proceso.pot_tec_bioq_planta/2
            else:
                punit=proceso.pot_tec_bioq_planta
            proceso.punit = punit

            cap1, proceso.tec_final1 = PROCESO_E2F2(proceso, punit)#RT Bioquimica - obtener tec final y cap 
            proceso.cap_planta1, proceso.cant_plantas1,proceso.comentario_cantplantas1, proceso.comentario_cubrimiento_planta1 = capacidad_y_cantidad_plantasFP2(proceso  , cap1, punit) #FP2
            calculo_costos(proceso)



            if proceso.pot_tec_termo_planta>=0.2:
                punit=proceso.pot_tec_termo_planta/2
            else:
                punit=proceso.pot_tec_termo_planta
            proceso.punit = punit

            cap2, proceso.tec_final2 = PROCESO_E1F1(proceso, punit) #RT Termoquimica - obtener tec final y cap 
            proceso.cap_planta2, proceso.cant_plantas2,proceso.comentario_cantplantas2, proceso.comentario_cubrimiento_planta2 = capacidad_y_cantidad_plantasFP3(proceso  , cap2 , punit) #FP3
            calculo_costos(proceso)



        if proceso.caso=='caso5':   
            if proceso.pot_tec_bioq_planta>=0.2:
                punit=proceso.pot_tec_bioq_planta/2
            else:
                punit=proceso.pot_tec_bioq_planta
            proceso.punit = punit
            cap, tec_final = PROCESO_E2F2(proceso, punit)
            capacidad_y_cantidad_plantasFP2(proceso  , cap , punit)
            
        
        if proceso.caso=='caso6':
            if proceso.pot_tec_termo_planta>=0.2:
                punit=proceso.pot_tec_termo_planta/2
            else:
                punit=proceso.pot_tec_termo_planta
            proceso.punit = punit
            
            cap, tec_final = PROCESO_E1F1(proceso, punit) #RT Termoquimica - obtener tec final y cap 
            capacidad_y_cantidad_plantasFP3(proceso  , cap , punit)
        
  


        # Guardamos los resultados
        calculo_costos(proceso)
        proceso.save()


    else:
        visual = False

    comentario_resultado(proceso)

    context = {
            'proceso': proceso,
            'visual': visual,
        
        }
    return render(request, "resultados.html", context)





