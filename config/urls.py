from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(f'{settings.ADMIN_URL}', admin.site.urls),
    path(
        'availability/',
        include('boatsandjoy_api.availability.urls', namespace='availability'),
    ),
    path(
        'bookings/',
        include('boatsandjoy_api.bookings.urls', namespace='bookings'),
    ),
    path('ht/', include('health_check.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
