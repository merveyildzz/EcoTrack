from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="EcoTrack API",
      default_version='v1',
      description="Carbon footprint tracking application API",
      terms_of_service="https://www.ecotrack.app/terms/",
      contact=openapi.Contact(email="support@ecotrack.app"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

def api_root(request):
    return JsonResponse({
        'message': 'EcoTrack API is running',
        'version': 'v1',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'activities': '/api/v1/activities/',
            'ai': '/api/v1/ai/',
            'social': '/api/v1/social/',
            'swagger': '/swagger/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API endpoints
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/activities/', include('activities.urls')),
    path('api/v1/ai/', include('ai_recommendations.urls')),
    path('api/v1/social/', include('social.urls')),
    
    # Health check
    path('health/', lambda request: JsonResponse({'status': 'OK'})),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)