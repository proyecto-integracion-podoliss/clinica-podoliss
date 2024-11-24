from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .forms import RegistroForm

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
    success_url = reverse_lazy('login')  # Redirigir al login después del registro


class PacienteView(LoginRequiredMixin, TemplateView):
    template_name = 'roles/pagina_paciente.html'

    def dispatch(self, request, *args, **kwargs):
        # Redirige a la página correspondiente si el rol no es paciente
        if request.user.rol != 'paciente':
            return redirect('pagina_profesional')  # O algún otro manejo
        return super().dispatch(request, *args, **kwargs)
    

class ProfesionalView(LoginRequiredMixin, TemplateView):
    template_name = 'roles/pagina_profesional.html'

    def dispatch(self, request, *args, **kwargs):
        # Redirige a la página correspondiente si el rol no es profesional
        if request.user.rol != 'profesional':
            return redirect('pagina_paciente')  # O algún otro manejo
        return super().dispatch(request, *args, **kwargs)