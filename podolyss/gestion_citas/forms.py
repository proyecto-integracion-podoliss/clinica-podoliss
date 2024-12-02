from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Agenda, Cita, Paciente, Centro, Profesional
from datetime import datetime

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'paciente'  # Asignamos el rol de paciente por defecto
        if commit:
            user.save()
        return user


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['tipo_documento', 'documento', 'prevision']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Documento de Identidad'}),
            'prevision': forms.Select(attrs={'class': 'form-select'}),
        }


class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'dias_disponibles', 'dias_excluidos', 'capacidad_maxima', 'activo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'dias_disponibles': forms.TextInput(attrs={'placeholder': 'Ejemplo: Lunes, Miércoles'}),
            'dias_excluidos': forms.TextInput(attrs={'placeholder': 'Ejemplo: Martes, Jueves'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'hora_inicio': 'Hora de Inicio',
            'hora_fin': 'Hora de Fin',
            'dias_disponibles': 'Días Disponibles',
            'dias_excluidos': 'Días Excluidos (opcional)',
            'capacidad_maxima': 'Capacidad Máxima por Horario',
            'activo': '¿Agenda Activa?',
        }


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['profesional', 'fecha_cita', 'hora_cita', 'observaciones', 'estado']
        widgets = {
            'profesional': forms.Select(attrs={'class': 'form-control'}),
            'fecha_cita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_cita': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Añadir observaciones'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Capturamos el usuario
        super().__init__(*args, **kwargs)

        # Ocultar el campo 'estado' si el usuario no es profesional ni administrador
        if self.user and self.user.rol not in ['profesional', 'administrador']:
            self.fields.pop('estado')

        # Validar antes de acceder al campo 'profesional'
        if 'profesional' in self.fields:
            # Filtrar los profesionales disponibles
            self.fields['profesional'].queryset = Profesional.objects.all()

        # Ocultar observaciones si no es profesional
        if self.user and self.user.rol != 'profesional' and 'observaciones' in self.fields:
            self.fields.pop('observaciones')
    
class CitaFormProfesional(forms.ModelForm):
    buscar_paciente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar paciente (nombre o documento)'}),
        label="Buscar Paciente"
    )

    class Meta:
        model = Cita
        fields = ['paciente', 'fecha_cita', 'hora_cita', 'observaciones', 'estado']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'fecha_cita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_cita': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Añadir observaciones'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Capturamos el usuario
        super().__init__(*args, **kwargs)

        # Limitar los pacientes disponibles al profesional
        if 'paciente' in self.fields:
            self.fields['paciente'].queryset = Paciente.objects.all()

    def clean_buscar_paciente(self):
        # Implementar lógica de búsqueda de pacientes si es necesario
        buscar_paciente = self.cleaned_data.get('buscar_paciente')
        return buscar_paciente