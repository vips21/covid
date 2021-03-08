from rest_framework import routers
from .views import (
    UserViewSet
)

app_name = 'account'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = []
urlpatterns += router.urls