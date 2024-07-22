from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    history,
    register,
    logout_view,
    login_view,
    city_autocomplete,
    index
)

urlpatterns = [
    path('', index, name='index'),
    path('history/', history, name='history'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('city_autocomplete/', city_autocomplete, name='city_autocomplete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
