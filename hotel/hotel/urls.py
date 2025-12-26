"""
URL configuration for hotel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from room.views import HotelsViewSet, RoomTypesViewSet, RoomsViewSet, GuestsViewSet, BookingsViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'hotels', HotelsViewSet, basename='hotel')

router_room_type = routers.DefaultRouter()
router_room_type.register(r'room_types', RoomTypesViewSet, basename='room_types')

router_rooms = routers.DefaultRouter()
router_rooms.register(r'rooms', RoomsViewSet, basename='rooms')

router_guests = routers.DefaultRouter()
router_guests.register(r'guests', GuestsViewSet, basename='guests')


router_bookings = routers.DefaultRouter()
router_bookings.register(r'bookings', BookingsViewSet, basename='bookings')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include(router_room_type.urls)),
    path('api/v1/', include(router_rooms.urls)),
    path('api/v1/', include(router_guests.urls)),
    path('api/v1/', include(router_bookings.urls))
]

