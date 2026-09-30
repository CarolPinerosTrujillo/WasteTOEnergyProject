# WasteTOEnergyProject

Aplicación de Diseño de Centros de Generación Distribuida - Biomasa residual ZNI de Colombia

Herramienta web que evalúa la viabilidad, el potencial energético de la biomasa residual
(agrícola, pecuaria, RSU y RSUO), la demanda energética de un centro de consumo y la
ruta tecnológica recomendada (termoquímica o bioquímica) para las Zonas No Interconectadas
de Colombia.

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

## Tests

```bash
python manage.py test
```

## Despliegue en Render

Repositorio: https://github.com/CarolPinerosTrujillo/WasteTOEnergyProject

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start command: `python manage.py migrate --noinput && gunicorn Biomasa.wsgi:application`
- Variables de entorno: `DEBUG=False`, `SECRET_KEY` (generada), `ALLOWED_HOSTS=.onrender.com`
- El archivo `.python-version` fija Python 3.11.

Cada `push` a `main` publica los cambios automáticamente.
