from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpRequest


def index(request: HttpRequest):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('gerenciar_clientes')
        return redirect('solicitar_exames')
    return redirect('login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('', include('exams.urls')),
    path('', include('empresarial.urls')),
    path('', index, name='index')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
