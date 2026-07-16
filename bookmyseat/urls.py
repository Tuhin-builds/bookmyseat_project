from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from movies import views
urlpatterns = [
    path('admin/analytics/', views.admin_analytics, name='admin_analytics'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('',include('users.urls')),
    path('movies/', include('movies.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)