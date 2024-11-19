from django.views.generic import TemplateView


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