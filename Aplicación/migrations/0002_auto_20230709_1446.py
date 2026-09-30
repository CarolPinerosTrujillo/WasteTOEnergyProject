from pathlib import Path

from django.db import migrations
import csv

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / 'fixtures'

def cargar_datos_residuos_agricolas(apps, schema_editor):
    residuos = apps.get_model('Aplicación', 'Residuos_agricolas')

    with open(FIXTURES_DIR / 'residuos_agricolas.csv', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        next(lector_csv)  # Saltar la primera fila (nombres de los campos)

        for fila in lector_csv:
            cultivo, residuo, fr, ybas, dr, pci, pb, wf = fila
            residuos.objects.create(cultivo=cultivo, residuo=residuo, fr=fr, ybas=ybas, dr=dr, pci=pci, pb=pb, wf=wf)

def cargar_datos_rendimientos_agricolas(apps, schema_editor):
    rendimientos = apps.get_model('Aplicación', 'Rendimientos_agricolas')

    with open(FIXTURES_DIR / 'rendimientos_agricolas.csv', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        next(lector_csv) 

        for fila in lector_csv:
            region, departamento, cultivo, rc = fila
            rendimientos.objects.create(region=region, departamento=departamento, cultivo=cultivo, rc=rc)


def cargar_datos_residuos_pecuarios(apps, schema_editor):
    residuos = apps.get_model('Aplicación', 'Residuos_pecuarios')

    with open(FIXTURES_DIR / 'residuos_pecuarios.csv', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        next(lector_csv)  

        for fila in lector_csv:
            animal, tipo, pb, pe, dr = fila
            residuos.objects.create(animal=animal, tipo=tipo, pb=pb, pe=pe, dr=dr)

def cargar_datos_produccion_rsu(apps, schema_editor):
    residuos = apps.get_model('Aplicación', 'Produccion_rsu')

    with open(FIXTURES_DIR / 'produccion_rsu.csv', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        next(lector_csv)  

        for fila in lector_csv:
            region, pro_RSU_hab, dr = fila
            residuos.objects.create(region=region, pro_RSU_hab=pro_RSU_hab, dr=dr)

def cargar_datos_tipo_rsuo(apps, schema_editor):
    residuos = apps.get_model('Aplicación', 'Tipo_rsuo')

    with open(FIXTURES_DIR / 'tipo_rsuo.csv', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        next(lector_csv)  

        for fila in lector_csv:
            tipo, pb, dr = fila
            residuos.objects.create(tipo=tipo, pb=pb, dr=dr)

class Migration(migrations.Migration):

    dependencies = [
        ('Aplicación', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(cargar_datos_residuos_agricolas),
        migrations.RunPython(cargar_datos_rendimientos_agricolas),
        migrations.RunPython(cargar_datos_residuos_pecuarios),
        migrations.RunPython(cargar_datos_produccion_rsu),
        migrations.RunPython(cargar_datos_tipo_rsuo),
    ]