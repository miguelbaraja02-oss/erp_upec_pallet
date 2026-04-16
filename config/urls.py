"""
URL configuration for config project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:login_page')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('', include('core.urls')),
    path('companies/', include('companies.urls')),
    path('accounts/', include('allauth.urls')),
    path('store/', include('store.urls')),
    path('recepcion/', include(('recepcion.urls', 'recepcion'), namespace='recepcion')),
    path('documentos/', include(('documentos.urls', 'documentos'), namespace='documentos')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
