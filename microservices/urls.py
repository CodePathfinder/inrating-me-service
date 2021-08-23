from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('api_gifts.urls')),
    path('v1/', include('me.urls'))
]
