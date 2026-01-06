from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # plants app
    path('', include('plants.urls')),

    # authentication ONLY
    path('accounts/', include('allauth.urls')),

    # cart ONLY
    path('cart/', include('accounts.urls')),

    path('payments/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


