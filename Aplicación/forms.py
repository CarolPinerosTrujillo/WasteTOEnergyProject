from django import forms
from django.db.models import Q
from .models import *

class ViabilidadForm(forms.ModelForm):

    class Meta:
        model = Proceso
        fields = ['region', 'distancia']

    def __init__(self, *args, **kwargs):
        super(ViabilidadForm, self).__init__(*args, **kwargs)
        self.fields['region'].widget.attrs['class'] = 'custom-select'
        self.fields['distancia'].widget.attrs['class'] = 'custom-input'
        self.fields['distancia'].widget.attrs['min'] = '0'

        self.fields['region'].required = True
        self.fields['distancia'].required = True

class ResiduosAgricolasForm(forms.Form):
    hectareas = forms.FloatField(widget=forms.NumberInput(attrs={'min': 0,'class': 'custom-input'}))

    def __init__(self, *args, **kwargs):
        proceso = kwargs.pop('proceso', None)
        super().__init__(*args, **kwargs)
        
        # Obtener todos los cultivos sin duplicados
        cultivos = Residuos_agricolas.objects.values_list('cultivo', flat=True).distinct()
        
        # Crear las opciones para el primer input de selección
        self.fields['cultivo'] = forms.ChoiceField(choices=[('', 'Seleccione un cultivo')] + [(cultivo, cultivo) for cultivo in cultivos],
                                                   widget=forms.Select(attrs={'onchange': 'this.form.submit();','class':'custom-select'}))
        
        # Crear el segundo input de selección
        if not self.data.get('cultivo'):
            self.fields['residuo'] = forms.ChoiceField(choices=[('', 'Seleccione un residuo')], disabled=True)
            self.fields['residuo'].widget.attrs['class'] = 'custom-select'
        else:
            residuos = Residuos_agricolas.objects.filter(cultivo=self.data.get('cultivo')).values_list('residuo', flat=True).distinct()
            
            # Actualizar las opciones del segundo input de selección
            self.fields['residuo'] = forms.ChoiceField(choices=[('', 'Seleccione un residuo')] + [(residuo, residuo) for residuo in residuos])
            self.fields['residuo'].widget.attrs['class'] = 'custom-select'

        # Obtener todos los departamentos sin duplicados
        departamentos = Rendimientos_agricolas.objects.filter(Q(region=proceso.region) | Q(region='general')).values_list('departamento', flat=True).distinct()
        
        # Crear las opciones para departamento
        self.fields['departamento'] = forms.ChoiceField(choices=[('', 'Seleccione un departamento')] + [(departamento, departamento) for departamento in departamentos])
        self.fields['departamento'].widget.attrs['class'] = 'custom-select'

class ResiduosPecuariosForm(forms.Form):
    cantidad = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 0,'class': 'custom-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obtener todos los anaimales sin duplicados
        animales = Residuos_pecuarios.objects.values_list('animal', flat=True).distinct()
        
        # Crear las opciones para el primer input de selección
        self.fields['animal'] = forms.ChoiceField(choices=[('', 'Seleccione un animal')] + [(animal, animal) for animal in animales],
                                                   widget=forms.Select(attrs={'onchange': 'this.form.submit();','class':'custom-select'}))
        
        # Crear el segundo input de selección
        if not self.data.get('animal'):
            self.fields['tipo'] = forms.ChoiceField(choices=[('', 'Seleccione un tipo')], disabled=True)
            self.fields['tipo'].widget.attrs['class'] = 'custom-select'
        else:
            tipos = Residuos_pecuarios.objects.filter(animal=self.data.get('animal')).values_list('tipo', flat=True).distinct()
            
            # Actualizar las opciones del segundo input de selección
            self.fields['tipo'] = forms.ChoiceField(choices=[('', 'Seleccione un tipo')] + [(tipo, tipo) for tipo in tipos])
            self.fields['tipo'].widget.attrs['class'] = 'custom-select'

class CantidadRSUForm(forms.Form):
    cant_personas = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 0,'class': 'custom-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # Obtener todos los cultivos sin duplicados
        regiones = Produccion_rsu.objects.values_list('region', flat=True).distinct()
        
        # Crear las opciones para el primer input de selección
        self.fields['region'] = forms.ChoiceField(
            choices=[('', 'Seleccione una región')] + [(region, region) for region in regiones],
            widget=forms.Select(attrs={'class':'custom-select'})
        )
        
class ResiduosRSUForm(forms.Form):
    masa_RSU = forms.FloatField(widget=forms.NumberInput(attrs={'min': 0,'class': 'custom-input'}))


class ResiduosRSUOForm(forms.Form):
    masa_RSUO = forms.FloatField(widget=forms.NumberInput(attrs={'min': 0,'class': 'custom-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # Obtener todos los cultivos sin duplicados
        tipos = Tipo_rsuo.objects.values_list('tipo', flat=True).distinct()
        
        # Crear las opciones para el primer input de selección
        self.fields['tipo'] = forms.ChoiceField(
            choices=[('', 'Seleccione un tipo')] + [(tipo, tipo) for tipo in tipos],
            widget=forms.Select(attrs={'class':'custom-select'})
        )

class CantidadDemandaForm(forms.Form):
    cant_hab = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 0,'class': 'custom-input'}))

class DemandaForm(forms.Form):
    ed = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 0,'class': 'custom-input'}))