from django.contrib import admin
from django.urls import path
from gestion_citas.views import LandingPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing_page'),
]
