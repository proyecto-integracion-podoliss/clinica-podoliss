from django.contrib import admin
from .models import Usuario, Paciente, Profesional, Administrador, Cita, Agenda, HistorialClinico, Notificacion, Auditoria, Centro, Prevision, TipoDocumento

# Personalización del administrador para el modelo Usuario
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'telefono', 'is_active')
    list_filter = ('rol', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'telefono')
    ordering = ('date_joined',)

# Registro de Paciente
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_telefono', 'get_email', 'nhc', 'documento', 'prevision')
    search_fields = ('usuario__username', 'usuario__email', 'nhc', 'documento')
    list_filter = ('usuario__is_active', 'prevision')

    @admin.display(ordering='usuario__telefono', description='Teléfono')
    def get_telefono(self, obj):
        return obj.usuario.telefono

    @admin.display(ordering='usuario__email', description='Email')
    def get_email(self, obj):
        return obj.usuario.email

# Registro de Profesional
@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'especialidad', 'get_telefono', 'get_email')
    search_fields = ('usuario__username', 'especialidad')
    list_filter = ('especialidad',)

    @admin.display(ordering='usuario__telefono', description='Teléfono')
    def get_telefono(self, obj):
        return obj.usuario.telefono

    @admin.display(ordering='usuario__email', description='Email')
    def get_email(self, obj):
        return obj.usuario.email

# Registro de Administrador
@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('usuario',)
    search_fields = ('usuario__username', 'usuario__email')

# Registro de Citas
from django.contrib import admin
from django.core.mail import send_mail
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'profesional', 'centro', 'fecha_hora', 'estado')  # Mostrar columnas en el admin
    list_filter = ('estado', 'fecha_cita', 'centro', 'profesional')  # Filtros
    search_fields = ('paciente__usuario__username', 'profesional__usuario__username', 'centro__nombre')  # Búsqueda
    date_hierarchy = 'fecha_cita'  # Navegación por fechas
    list_editable = ('estado',)  # Permitir edición del estado directamente desde la lista

    @admin.display(description='Fecha y Hora')
    def fecha_hora(self, obj):
        return f"{obj.fecha_cita} {obj.hora_cita}"

   

    

       



# Registro de Agenda
@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('profesional', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('activo', 'profesional')
    search_fields = ('profesional__usuario__username',)
    date_hierarchy = 'fecha_inicio'

# Registro de Historial Clínico
@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'profesional', 'fecha_registro')
    list_filter = ('fecha_registro', 'profesional')
    search_fields = ('paciente__usuario__username', 'descripcion')
    date_hierarchy = 'fecha_registro'

# Registro de Notificaciones
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensaje', 'fecha_envio', 'estado')
    list_filter = ('estado', 'fecha_envio')
    search_fields = ('usuario__username', 'mensaje')
    date_hierarchy = 'fecha_envio'

# Registro de Auditoría
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'fecha')
    list_filter = ('fecha', 'usuario')
    search_fields = ('usuario__username', 'accion', 'descripcion')
    date_hierarchy = 'fecha'

# Registro de Centros
@admin.register(Centro)
class CentroAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'telefono')
    search_fields = ('nombre', 'direccion')
    list_filter = ('nombre',)


# Registro de Prevision
@admin.register(Prevision)
class PrevisionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


# Registro de TipoDocumento
@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)