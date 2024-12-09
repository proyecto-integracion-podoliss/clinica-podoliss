from django.views.generic import TemplateView, CreateView, ListView,DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from .forms import CitaFormProfesional, RegistroForm, AgendaForm, CitaForm, PacienteForm
from .models import Agenda, Cita, Paciente, Profesional, Centro
from datetime import datetime
from django.contrib import messages  #sweet alert
from django.db.models import Q
from django.utils.timezone import now


class LandingPageView(TemplateView):
    template_name = "landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Bienvenido a Podolyss"
        context['caracteristicas'] = [
            "Gestión de pacientes y profesionales",
            "Agendamiento intuitivo",
            "Notificaciones y recordatorios",
        ]
        return context
    

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        if self.request.user.rol == 'paciente':
            return reverse_lazy('pagina_paciente')
        elif self.request.user.rol == 'profesional':
            return reverse_lazy('pagina_profesional')
        else:
            return reverse_lazy('landing_page')
    

class RegistroView(CreateView):
    template_name = 'registration/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('login') # Redirigir al login después del registro

#CRUD DE PACIENTES.==============================
@method_decorator(login_required, name='dispatch')
class PacienteView(TemplateView):
    template_name = 'roles/pagina_paciente.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol != 'paciente':
            return redirect('landing_page')
        return super().dispatch(request, *args, **kwargs)
    
@method_decorator(login_required, name='dispatch')    
class PacienteCreateView(LoginRequiredMixin, CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'roles/editar_paciente.html'
    success_url = reverse_lazy('pagina_paciente')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class PacienteDatosView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = 'roles/datos_paciente.html'
    context_object_name = 'paciente'

    def get_object(self):
        # Obtiene el paciente asociado al usuario autenticado
        return get_object_or_404(Paciente, usuario=self.request.user)

@method_decorator(login_required, name='dispatch')
class PacienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'roles/editar_paciente.html'
    success_url = reverse_lazy('pagina_paciente')

    def get_object(self):
        return get_object_or_404(Paciente, usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, '¡Información actualizada con éxito!')
        return super().form_valid(form)

#CRUD DE PROFESIONES.==============================
@method_decorator(login_required, name='dispatch')
class ProfesionalView(TemplateView):
    template_name = 'roles/pagina_profesional.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol != 'profesional':
            return redirect('landing_page')
        return super().dispatch(request, *args, **kwargs)

#CRUD DE AGENDA.==================================
@method_decorator(login_required, name='dispatch')
class AgendaListView(LoginRequiredMixin, ListView):
    model = Agenda
    template_name = 'gestion_agendas/lista_agendas.html'
    context_object_name = 'agendas'

    def get_queryset(self):
        # Filtra las agendas del profesional que está autenticado
        if self.request.user.rol == 'profesional':
            return Agenda.objects.filter(profesional__usuario=self.request.user).order_by('fecha_inicio', 'hora_inicio')
        return Agenda.objects.none()  # Si no es profesional, no devuelve nada
    
@method_decorator(login_required, name='dispatch')
class CrearAgendaView(LoginRequiredMixin, CreateView):
    model = Agenda
    form_class = AgendaForm
    template_name = 'gestion_agendas/crear_agenda.html'
    success_url = reverse_lazy('pagina_profesional')  # Redirige al panel profesional tras crear una agenda

    def form_valid(self, form):
        # Asigna automáticamente el profesional al usuario autenticado
        if self.request.user.rol == 'profesional':
            form.instance.profesional = self.request.user.profesional
            messages.success(self.request, '¡Agenda creada con éxito!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'No tienes permisos para crear una agenda.')
            return redirect('pagina_paciente')  # Redirige si el usuario no es un profesional

@method_decorator(login_required, name='dispatch')
class AgendaUpdateView(UpdateView):
    model = Agenda
    fields = ['profesional', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'dias_disponibles', 'dias_excluidos', 'capacidad_maxima', 'activo']
    template_name = 'gestion_agendas/editar_agenda.html'
    success_url = reverse_lazy('agenda_list')
    def form_valid(self, form):
        # Envía un mensaje de éxito
        messages.success(self.request, 'Agenda actualizada con éxito!')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Envía un mensaje de error
        messages.error(self.request, 'Hubo un error al intentar actualizar la agenta. Por favor, verifica los datos.')
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class AgendaDeleteView(DeleteView):
    model = Agenda
    template_name = 'gestion_agendas/eliminar_agenda.html'
    success_url = reverse_lazy('agenda_list')
    def form_valid(self, form):
        # Envía un mensaje de éxito
        messages.success(self.request, 'Agenda cancelada con éxito!')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Envía un mensaje de error
        messages.error(self.request, 'Hubo un error al intentar actualizar la cita. Por favor, verifica los datos.')
        return super().form_invalid(form)
    

#CRUD DE CITAS.=====================================
@method_decorator(login_required, name='dispatch')
class CitaListView(ListView):
    model = Cita
    template_name = 'gestion_citas/listar_citas.html'
    context_object_name = 'citas'

    def get_queryset(self):
        """
        Filtrar las citas desde el día de hoy en adelante.
        """
        user = self.request.user
        fecha_hoy = now().date()  # Obtiene la fecha actual (sin hora)

        if user.rol == 'paciente':
            return Cita.objects.filter(
                paciente__usuario=user,
                fecha_cita__gte=fecha_hoy  # Filtra las citas a partir de hoy
            ).order_by('fecha_cita', 'hora_cita')
        elif user.rol == 'profesional':
            return Cita.objects.filter(
                profesional__usuario=user,
                fecha_cita__gte=fecha_hoy  # Filtra las citas a partir de hoy
            ).order_by('fecha_cita', 'hora_cita')

        return Cita.objects.none()  # No mostrar citas si el usuario no tiene un rol válido.

    
@method_decorator(login_required, name='dispatch')
class CitaCreateView(CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "gestion_citas/crear_cita.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasar el usuario al formulario
        return kwargs

    def form_valid(self, form):
        try:
            form.instance.paciente = self.request.user.paciente
            form.instance.centro = Centro.objects.first()
            agenda_activa = Agenda.objects.filter(
                profesional=form.instance.profesional,
                fecha_inicio__lte=form.instance.fecha_cita,
                fecha_fin__gte=form.instance.fecha_cita,
                activo=True
            ).exists()
            if not agenda_activa:
                raise ValueError("El profesional no tiene una agenda activa para la fecha seleccionada.")
            
            messages.success(self.request, "La solicitud se creó correctamente.")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Lo sentimos: {e}")
            return self.form_invalid(form)


    def get_success_url(self):
        # Redirigir según el rol del usuario
        return reverse_lazy('pagina_paciente') if self.request.user.rol == 'paciente' else reverse_lazy('pagina_profesional')

    

@method_decorator(login_required, name='dispatch')
class CitaUpdateView(UpdateView):
    model = Cita
    fields = ['fecha_cita', 'hora_cita', 'observaciones', 'estado']
    template_name = 'gestion_citas/editar_cita.html'
    success_url = '/citas/list/'

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'paciente':
            return Cita.objects.filter(paciente__usuario=user)
        elif user.rol == 'profesional':
            return Cita.objects.filter(profesional__usuario=user)
        return Cita.objects.none()

    def form_valid(self, form):
        # Envía un mensaje de éxito
        messages.success(self.request, '¡Cita actualizada con éxito!')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Envía un mensaje de error
        messages.error(self.request, 'Hubo un error al intentar actualizar la cita. Por favor, verifica los datos.')
        return super().form_invalid(form)
    
@method_decorator(login_required, name='dispatch')
class CitaDeleteView(DeleteView):
    model = Cita
    template_name = 'gestion_citas/eliminar_cita.html'
    success_url = '/citas/list/'  # Redirige a la lista de citas después de eliminar

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'paciente':
            return Cita.objects.filter(paciente__usuario=user)
        elif user.rol == 'profesional':
            return Cita.objects.filter(profesional__usuario=user)
        return Cita.objects.none()
    def form_valid(self, form):
        # Envía un mensaje de éxito
        messages.success(self.request, '¡Cita Cancelada con exito!')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Envía un mensaje de error
        messages.error(self.request, 'Hubo un error al intentar actualizar la cita. Por favor, verifica los datos.')
        return super().form_invalid(form)

#HISTORIALES.============================================
@method_decorator(login_required, name='dispatch')
class PacienteHistorialCitasView(ListView):
    model = Cita
    template_name = 'gestion_citas/historialpac.html'
    context_object_name = 'citas'
    paginate_by = 10

    def get_queryset(self):
        queryset = Cita.objects.filter(paciente__usuario=self.request.user).distinct().order_by('fecha_cita', 'hora_cita')
        mes = self.request.GET.get('mes')
        if mes:
            try:
                mes = int(mes)
                queryset = queryset.filter(fecha_cita__month=mes)
            except ValueError:
                pass
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = [
            (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
            (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
            (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
        ]
        context['paginacion'] = True
        return context
    

@method_decorator(login_required, name='dispatch')
class ProfesionalHistorialCitasView(ListView):
    model = Cita
    template_name = 'gestion_citas/historialprof.html'
    context_object_name = 'citas'

    def get_queryset(self):
        """
        Filtra las citas asociadas al profesional autenticado por nombre de paciente y rango de fechas,
        basado en la fecha de inicio de las citas.
        """
        profesional = Profesional.objects.get(usuario=self.request.user)
        queryset = Cita.objects.filter(profesional=profesional).select_related('paciente').order_by('-fecha_cita', '-hora_cita')

        # Captura los parámetros del formulario
        nombre_paciente = self.request.GET.get('nombre_paciente', '').strip()
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        # Filtrar por nombre del paciente
        if nombre_paciente:
            queryset = queryset.filter(paciente__usuario__first_name__icontains=nombre_paciente)

        # Filtrar por rango de fechas basado en la fecha de inicio
        if fecha_inicio and fecha_fin:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

                if fecha_inicio_dt > fecha_fin_dt:
                    messages.error(self.request, "La fecha de inicio no puede ser mayor que la fecha de fin.")
                else:
                    # Filtro basado en fecha de inicio de la cita
                    queryset = queryset.filter(fecha_cita__gte=fecha_inicio_dt, fecha_cita__lte=fecha_fin_dt)
            except ValueError:
                messages.error(self.request, "Formato de fecha inválido. Por favor, seleccione fechas válidas.")

        return queryset



# @method_decorator(login_required, name='dispatch')
# class ProfesionalHistorialCitasView(ListView):
#     model = Cita
#     template_name = 'gestion_citas/historialprof.html'
#     context_object_name = 'citas'

#     def get_queryset(self):
#         # Filtra las citas para el profesional autenticado
#         profesional = Profesional.objects.get(usuario=self.request.user)
#         queryset = Cita.objects.filter(profesional=profesional).select_related('paciente', 'agenda').order_by('-fecha_cita', '-hora_cita')

#         # Captura los parámetros del formulario
#         nombre_paciente = self.request.GET.get('nombre_paciente', '').strip()
#         fecha_inicio = self.request.GET.get('fecha_inicio')
#         fecha_fin = self.request.GET.get('fecha_fin')

#         # Filtrado por nombre del paciente
#         if nombre_paciente:
#             queryset = queryset.filter(
#                 Q(paciente__usuario__first_name__icontains=nombre_paciente) |
#                 Q(paciente__usuario__last_name__icontains=nombre_paciente)
#             )

#         # Filtrado por rango de fechas
#         if fecha_inicio and fecha_fin:
#             try:
#                 fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
#                 fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                
#                 if fecha_inicio_dt > fecha_fin_dt:
#                     messages.error(self.request, "La fecha de inicio no puede ser mayor que la fecha de fin.")
#                 else:
#                     queryset = queryset.filter(fecha_cita__gte=fecha_inicio_dt, fecha_cita__lte=fecha_fin_dt)
#             except ValueError:
#                 messages.error(self.request, "Formato de fecha inválido. Por favor, seleccione fechas válidas.")

#         return queryset

@method_decorator(login_required, name='dispatch')
class CitaCreateByProfesionalView(CreateView):
    model = Cita
    form_class = CitaFormProfesional
    template_name = "gestion_citas/crear_cita_profesional.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasar el usuario al formulario
        return kwargs

    def form_valid(self, form):
        try:
            # Asociar automáticamente el profesional y el centro
            form.instance.profesional = self.request.user.profesional
            form.instance.centro = Centro.objects.first()  # Asignar el único centro
            form.save()
            messages.success(self.request, "La cita se creó correctamente.")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error al crear la cita: {str(e)}")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        # Asegúrate de que solo se añada el mensaje de error si el formulario es inválido
        messages.error(self.request, "Error al crear la cita. Por favor, revisa los datos ingresados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('pagina_profesional')
    