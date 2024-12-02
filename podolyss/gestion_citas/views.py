from django.views.generic import TemplateView, CreateView, ListView
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
from django.contrib import messages


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


@method_decorator(login_required, name='dispatch')
class PacienteView(TemplateView):
    template_name = 'roles/pagina_paciente.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol != 'paciente':
            return redirect('landing_page')
        return super().dispatch(request, *args, **kwargs)
    
class PacienteCreateView(LoginRequiredMixin, CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'roles/editar_paciente.html'
    success_url = reverse_lazy('pagina_paciente')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class PacienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'roles/editar_paciente.html'
    success_url = reverse_lazy('pagina_paciente')

    def get_object(self):
        return get_object_or_404(Paciente, usuario=self.request.user)


@method_decorator(login_required, name='dispatch')
class ProfesionalView(TemplateView):
    template_name = 'roles/pagina_profesional.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol != 'profesional':
            return redirect('landing_page')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class AgendaListView(ListView):
    model = Agenda
    template_name = 'gestion_agendas/lista_agendas.html'
    context_object_name = 'agendas'

    def get_queryset(self):
        if self.request.user.rol == 'profesional':
            return Agenda.objects.filter(profesional__usuario=self.request.user).order_by('fecha_inicio', 'hora_inicio')
        return Agenda.objects.none()
    

@method_decorator(login_required, name='dispatch')
class CrearAgendaView(CreateView):
    model = Agenda
    form_class = AgendaForm
    template_name = 'gestion_agendas/crear_agenda.html'
    success_url = reverse_lazy('pagina_profesional')

    def form_valid(self, form):
        if self.request.user.rol == 'profesional':
            form.instance.profesional = self.request.user.profesional
            return super().form_valid(form)
        else:
            return redirect('pagina_paciente')
    

class AgendaListView(LoginRequiredMixin, ListView):
    model = Agenda
    template_name = 'gestion_agendas/lista_agendas.html'
    context_object_name = 'agendas'

    def get_queryset(self):
        # Filtra las agendas del profesional que está autenticado
        if self.request.user.rol == 'profesional':
            return Agenda.objects.filter(profesional__usuario=self.request.user).order_by('fecha_inicio', 'hora_inicio')
        return Agenda.objects.none()  # Si no es profesional, no devuelve nada
    

class CrearAgendaView(LoginRequiredMixin, CreateView):
    model = Agenda
    form_class = AgendaForm
    template_name = 'gestion_agendas/crear_agenda.html'
    success_url = reverse_lazy('pagina_profesional')  # Redirige al panel profesional tras crear una agenda

    def form_valid(self, form):
        # Asigna automáticamente el profesional al usuario autenticado
        if self.request.user.rol == 'profesional':
            form.instance.profesional = self.request.user.profesional
            return super().form_valid(form)
        else:
            return redirect('pagina_paciente')  # Redirige si el usuario no es un profesional


@method_decorator(login_required, name='dispatch')
class AgendaUpdateView(UpdateView):
    model = Agenda
    fields = ['profesional', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'dias_disponibles', 'dias_excluidos', 'capacidad_maxima', 'activo']
    template_name = 'gestion_agendas/editar_agenda.html'
    success_url = reverse_lazy('agenda_list')

@method_decorator(login_required, name='dispatch')
class AgendaDeleteView(DeleteView):
    model = Agenda
    template_name = 'gestion_agendas/eliminar_agenda.html'
    success_url = reverse_lazy('agenda_list')

@method_decorator(login_required, name='dispatch')
class CitaListView(ListView):
    model = Cita
    template_name = 'gestion_citas/listar_citas.html'
    context_object_name = 'citas'

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'paciente':
            return Cita.objects.filter(paciente__usuario=user).order_by('fecha_cita', 'hora_cita')
        elif user.rol == 'profesional':
            return Cita.objects.filter(profesional__usuario=user).order_by('fecha_cita', 'hora_cita')
        return Cita.objects.none() #No mostrar citas si el usuario no tiene un rol válido
    

from django.contrib import messages

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
            # Asociar automáticamente el paciente y el único centro disponible
            form.instance.paciente = self.request.user.paciente
            form.instance.centro = Centro.objects.first()  # Asignar el único centro
            # Verificar si el profesional tiene una agenda activa para la fecha seleccionada
            agenda_activa = Agenda.objects.filter(
                profesional=form.instance.profesional,
                fecha_inicio__lte=form.instance.fecha_cita,
                fecha_fin__gte=form.instance.fecha_cita,
                activo=True
            ).exists()
            if not agenda_activa:
                raise ValueError("El profesional no tiene una agenda activa para la fecha seleccionada.")

            messages.success(self.request, "La cita se creó correctamente.")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error al crear la cita: {e}")
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
class ProfesionalHistorialAgendasView(ListView):
    model = Agenda
    template_name = 'gestion_citas/historialprof.html'
    context_object_name = 'agendas'

    def get_queryset(self):
        # Filtra las agendas para el profesional autenticado
        profesional = Profesional.objects.get(usuario=self.request.user)
        queryset = Agenda.objects.filter(profesional=profesional).distinct().order_by('fecha_inicio', 'hora_inicio')
        
        # Filtro por mes si se proporciona
        mes = self.request.GET.get('mes')
        if mes:
            try:
                mes = int(mes)
                queryset = queryset.filter(fecha_inicio__month=mes)
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
        return context
        

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
    