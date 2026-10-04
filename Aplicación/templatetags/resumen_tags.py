from django import template
from django.urls import reverse

from ..models import Proceso

register = template.Library()


@register.inclusion_tag('includes/reanudar.html', takes_context=True)
def boton_reanudar(context):
    request = context.get('request')
    if request is None:
        return {'url': reverse('iniciar_proceso'), 'etiqueta': 'EMPEZAR PROCESO'}
    proceso_id = request.session.get('proceso_id')
    proceso = None
    if proceso_id is not None:
        proceso = Proceso.objects.filter(id=proceso_id).first()
    if proceso is not None:
        url = request.session.get('ultima_url') or reverse('viabilidad', args=[proceso.id])
        return {'url': url, 'etiqueta': '▶ Reanudar proceso'}
    return {'url': reverse('iniciar_proceso'), 'etiqueta': 'EMPEZAR PROCESO'}
