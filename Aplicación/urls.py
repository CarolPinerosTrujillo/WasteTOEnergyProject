from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.introduccion,  name="introduccion"),
    path('inicio/', views.inicio,  name="inicio"),
    path('funcionamiento/', views.funcionamiento,  name="funcionamiento"),
    path('fuentes/', views.fuentes,  name="fuentes"),
    path('iniciar_proceso/', views.iniciar_proceso,  name="iniciar_proceso"),
    path('viabilidad/<int:proceso_id>', views.viabilidad,  name="viabilidad"),
    path('agricola/<int:proceso_id>', views.agricola,  name="agricola"),
    path('agricola/<int:proceso_id>/question', views.agricola_pregunta,  name="agricola_pregunta"),
    path('pecuaria/<int:proceso_id>', views.pecuaria,  name="pecuaria"),
    path('pecuaria/<int:proceso_id>/question', views.pecuaria_pregunta,  name="pecuaria_pregunta"),
    path('rsu/<int:proceso_id>', views.rsu,  name="rsu"),
    path('rsu/<int:proceso_id>/question', views.rsu_pregunta,  name="rsu_pregunta"),
    path('rsuo/<int:proceso_id>', views.rsuo,  name="rsuo"),
    path('rsuo/<int:proceso_id>/question', views.rsuo_pregunta,  name="rsuo_pregunta"),
    path('demanda/<int:proceso_id>', views.demanda,  name="demanda"),
    path('resultados/<int:proceso_id>', views.resultados,  name="resultados"),
] + static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
