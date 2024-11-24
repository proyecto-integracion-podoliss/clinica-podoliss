from django.contrib import admin
from django.urls import path
from gestion_citas.views import LandingPageView, CustomLoginView, RegistroView, PacienteView, ProfesionalView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing_page'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('paciente/', PacienteView.as_view(), name='pagina_paciente'),
    path('profesional/', ProfesionalView.as_view(), name='pagina_profesional'),
]
