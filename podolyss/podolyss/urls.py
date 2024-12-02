from django.contrib import admin
from django.urls import path
from gestion_citas.views import LandingPageView, CustomLoginView, RegistroView, PacienteView, ProfesionalView, AgendaListView, CrearAgendaView, AgendaUpdateView, AgendaDeleteView, CitaCreateView, PacienteCreateView, PacienteUpdateView,PacienteHistorialCitasView,ProfesionalHistorialAgendasView, CitaListView, CitaUpdateView, CitaDeleteView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing_page'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('paciente/', PacienteView.as_view(), name='pagina_paciente'),
    path('paciente/crear/', PacienteCreateView.as_view(), name='crear_paciente'),
    path('paciente/editar/', PacienteUpdateView.as_view(), name='editar_paciente'),
    path('profesional/', ProfesionalView.as_view(), name='pagina_profesional'),
    path('profesional/agendas/', AgendaListView.as_view(), name='agenda_list'),
    path('profesional/crear-agenda/', CrearAgendaView.as_view(), name='crear_agenda'),
    path('agenda/<int:pk>/editar/', AgendaUpdateView.as_view(), name='agenda_edit'),
    path('agenda/<int:pk>/eliminar/', AgendaDeleteView.as_view(), name='agenda_delete'),
    path('citas/crear/', CitaCreateView.as_view(), name='cita_create'),
    path('citas/list/', CitaListView.as_view(), name='cita_list'),
    path('citas/<int:pk>/editar/', CitaUpdateView.as_view(), name='cita_edit'),
    path('citas/<int:pk>/eliminar/', CitaDeleteView.as_view(), name='cita_delete'),
    path('historial/paciente/', PacienteHistorialCitasView.as_view(), name='historial_citas_paciente'),
    path('historial/profesional/', ProfesionalHistorialAgendasView.as_view(), name='historial_citas_profesional'),
]
