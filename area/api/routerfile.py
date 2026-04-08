from rest_framework.routers import DefaultRouter
from .views import AreaViewSet, SubAreaViewSet

######################### Declare our router #########################
router = DefaultRouter()

######################### Declare our Urls #########################
#### App zone ####
router.register(r"areas", AreaViewSet, basename="area")
router.register(r"sub-areas", SubAreaViewSet, basename="sub-area")