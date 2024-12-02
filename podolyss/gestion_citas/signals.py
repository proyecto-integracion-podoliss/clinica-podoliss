from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Cita


@receiver(pre_save, sender=Cita)
def enviar_correos_cambio_estado(sender, instance, **kwargs):
    # Verificar si la cita ya existe en la base de datos
    if instance.pk:
        # Obtener la cita anterior
        cita_anterior = Cita.objects.get(pk=instance.pk)

        # Si el estado cambia a CONFIRMADA
        if cita_anterior.estado != "CONFIRMADA" and instance.estado == "CONFIRMADA":
            enviar_correos_confirmacion(instance)

        # Si el estado cambia a CANCELADA
        elif cita_anterior.estado != "CANCELADA" and instance.estado == "CANCELADA":
            enviar_correos_cancelacion(instance)

        # Si el profesional realiza una modificación
        if hasattr(instance, '_user') and instance._user.rol == 'profesional':
            enviar_correos_modificacion(cita_anterior, instance)


def enviar_correos_confirmacion(cita):
    paciente = cita.paciente.usuario.email
    profesional = cita.profesional.usuario.email
    especialidad = cita.profesional.especialidad
    fecha_cita = cita.fecha_cita
    hora_cita = cita.hora_cita
    centro = cita.centro.nombre
    tipo_documento = cita.paciente.tipo_documento
    documento = cita.paciente.documento
    prevision = cita.paciente.prevision
    nombre_paciente = cita.paciente.usuario.get_full_name() or cita.paciente.usuario.username
    nombre_profesional = cita.profesional.usuario.get_full_name() or cita.profesional.usuario.username

    asunto_paciente = "Confirmación de cita - Clínica Podoliss"
    mensaje_paciente = f"""
    Estimado/a {nombre_paciente},

    Su cita ha sido confirmada:
    Fecha: {fecha_cita}
    Hora: {hora_cita}
    Centro: {centro}
    Profesional: {nombre_profesional}
    Especialidad: {especialidad}

    Gracias por confiar en Clínica Podoliss.
    """
    send_mail(asunto_paciente, mensaje_paciente, 'noreply@podoliss.com', [paciente])

    asunto_profesional = "Cita confirmada en su agenda"
    mensaje_profesional = f"""
    Estimado/a {nombre_profesional},

    Se ha confirmado una nueva cita:
    Paciente: {nombre_paciente}
    Fecha: {fecha_cita}
    Hora: {hora_cita}
    Centro: {centro}

    Por favor, revise su agenda.
    """
    send_mail(asunto_profesional, mensaje_profesional, 'noreply@podoliss.com', [profesional])


def enviar_correos_cancelacion(cita):
    paciente = cita.paciente.usuario.email
    profesional = cita.profesional.usuario.email
    fecha_cita = cita.fecha_cita
    hora_cita = cita.hora_cita
    centro = cita.centro.nombre
    tipo_documento = cita.paciente.tipo_documento
    documento = cita.paciente.documento
    prevision = cita.paciente.prevision
    nombre_paciente = cita.paciente.usuario.get_full_name() or cita.paciente.usuario.username
    nombre_profesional = cita.profesional.usuario.get_full_name() or cita.profesional.usuario.username

    asunto_paciente = "Cancelación de cita - Clínica Podoliss"
    mensaje_paciente = f"""
    Estimado/a {nombre_paciente},

    Lamentamos informarle que su cita ha sido cancelada:
    Fecha: {fecha_cita}
    Hora: {hora_cita}
    Centro: {centro}
    Profesional: {nombre_profesional}

    Gracias por confiar en Clínica Podoliss.
    """
    send_mail(asunto_paciente, mensaje_paciente, 'noreply@podoliss.com', [paciente])

    asunto_profesional = "Cancelación de cita en su agenda"
    mensaje_profesional = f"""
    Estimado/a {nombre_profesional},

    La cita con el paciente {nombre_paciente} ha sido cancelada:
    Fecha: {fecha_cita}
    Hora: {hora_cita}
    Centro: {centro}

    Por favor, ajuste su agenda.
    """
    send_mail(asunto_profesional, mensaje_profesional, 'noreply@podoliss.com', [profesional])


def enviar_correos_modificacion(cita_anterior, cita_actual):
    paciente = cita_actual.paciente.usuario.email
    profesional = cita_actual.profesional.usuario.email
    nombre_paciente = cita_actual.paciente.usuario.get_full_name() or cita_actual.paciente.usuario.username
    nombre_profesional = cita_actual.profesional.usuario.get_full_name() or cita_actual.profesional.usuario.username

    cambios = []
    if cita_anterior.fecha_cita != cita_actual.fecha_cita:
        cambios.append(f"Fecha: {cita_anterior.fecha_cita} → {cita_actual.fecha_cita}")
    if cita_anterior.hora_cita != cita_actual.hora_cita:
        cambios.append(f"Hora: {cita_anterior.hora_cita} → {cita_actual.hora_cita}")
    if cita_anterior.observaciones != cita_actual.observaciones:
        cambios.append(f"Observaciones: {cita_anterior.observaciones or 'N/A'} → {cita_actual.observaciones or 'N/A'}")

    cambios_texto = "\n".join(cambios) if cambios else "No se realizaron cambios significativos."

    asunto_paciente = "Modificación de cita - Clínica Podoliss"
    mensaje_paciente = f"""
    Estimado/a {nombre_paciente},

    Su cita ha sido modificada:
    {cambios_texto}

    Gracias por confiar en Clínica Podoliss.
    """
    send_mail(asunto_paciente, mensaje_paciente, 'noreply@podoliss.com', [paciente])

    asunto_profesional = "Confirmación de cambios en la cita"
    mensaje_profesional = f"""
    Estimado/a {nombre_profesional},

    Ha realizado modificaciones en la cita con el paciente {nombre_paciente}:
    {cambios_texto}

    Por favor, asegúrese de revisar los detalles actualizados.
    """
    send_mail(asunto_profesional, mensaje_profesional, 'noreply@podoliss.com', [profesional])
