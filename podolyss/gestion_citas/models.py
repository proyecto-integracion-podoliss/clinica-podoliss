from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Modelo de usuario personalizado
class Usuario(AbstractUser):
    ROLES = (
        ('paciente', 'Paciente'),
        ('profesional', 'Profesional'),
        ('administrador', 'Administrador'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='paciente')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.rol})"


# Modelo para centros
class Centro(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Centro")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, null=True, blank=True, verbose_name="Teléfono")
    email = models.EmailField(null=True, blank=True, verbose_name="Correo Electrónico")

    def __str__(self):
        return self.nombre


# Modelo para tipo de documento
class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=20, unique=True, verbose_name="Tipo de Documento")

    def __str__(self):
        return self.nombre


# Modelo para previsión
class Prevision(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre de Previsión")

    def __str__(self):
        return self.nombre


# Modelo para pacientes
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='paciente')
    nhc = models.CharField(max_length=20, unique=True, verbose_name="Número de Historia Clínica")
    documento = models.CharField(max_length=20, unique=True, verbose_name="Documento de Identidad")
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, verbose_name="Tipo de Documento")
    prevision = models.ForeignKey(Prevision, on_delete=models.CASCADE, verbose_name="Previsión de Salud")

    def save(self, *args, **kwargs):
        if not self.nhc:  # Generar NHC solo si no existe
            self.nhc = f"NHC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Paciente: {self.usuario.get_full_name()} ({self.nhc})"


# Modelo para historial clínico
class HistorialClinico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historial_clinico')
    profesional = models.ForeignKey('Profesional', on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_clinicos')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Historial: {self.paciente.usuario.get_full_name()} - {self.fecha_registro}"


# Modelo para profesionales
class Profesional(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='profesional')
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f"Profesional: {self.usuario.get_full_name()} - Especialidad: {self.especialidad}"


# Modelo para administradores
class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='administrador')

    def __str__(self):
        return f"Administrador: {self.usuario.get_full_name()}"


# Modelo para agenda
class Agenda(models.Model):
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='agendas')
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")
    dias_disponibles = models.CharField(max_length=50, verbose_name="Días Disponibles")  # Ejemplo: "Lunes, Miércoles, Viernes"
    dias_excluidos = models.CharField(max_length=50, null=True, blank=True, verbose_name="Días Excluidos")
    capacidad_maxima = models.PositiveIntegerField(default=1, verbose_name="Capacidad Máxima por Horario")
    activo = models.BooleanField(default=True, verbose_name="Agenda Activa")

    def __str__(self):
        return f"Agenda de {self.profesional} ({self.fecha_inicio} - {self.fecha_fin})"


# Modelo para citas
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='citas')
    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE, related_name='citas', null=True, blank=True)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, related_name='citas', verbose_name="Centro")
    estado = models.CharField(
        max_length=20,
        choices=[
            ("PENDIENTE", "Pendiente"),
            ("CONFIRMADA", "Confirmada"),
            ("CANCELADA", "Cancelada"),
        ],
        default="PENDIENTE",
        verbose_name="Estado de la Cita"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_cita = models.DateField(verbose_name="Fecha de la Cita")
    hora_cita = models.TimeField(verbose_name="Hora de la Cita")
    observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    def save(self, *args, **kwargs):
        # Validar capacidad disponible
        agenda = Agenda.objects.filter(
            profesional=self.profesional,
            activo=True,
            fecha_inicio__lte=self.fecha_cita,
            fecha_fin__gte=self.fecha_cita
        ).first()
        if not agenda:
            raise ValueError("El profesional no tiene una agenda activa para la fecha seleccionada.")

        super().save(*args, **kwargs)   


# Modelo para notificaciones
class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('ENVIADO', 'Enviado'),
            ('NO_ENVIADO', 'No Enviado'),
            ('LEIDO', 'Leído'),
        ],
        default='NO_ENVIADO',
    )

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.estado}"


# Modelo para auditoría
class Auditoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='auditorias')
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Auditoría: {self.usuario.username} - {self.accion}"
