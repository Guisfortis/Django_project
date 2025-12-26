# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Hotels, Room_types, Rooms, Guests, Bookings
from .serializers import HotelsSerializer, RoomTypesSerializer, RoomsSerializer, BookingsSerializer, GuestsSerializer
from django_filters.rest_framework import DjangoFilterBackend

class HotelsViewSet(viewsets.ModelViewSet):
    queryset = Hotels.objects.all()
    serializer_class = HotelsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['star_rating', 'country', 'city']

    @action(methods=['get'], detail=True)
    def room_types(self, request, pk=None):
        try:
            pk = Hotels.objects.get(pk=pk).id
        except Exception:
            return Response({'ОШИБКА': 'Такого отеля не существует!'})
        room_type = Room_types.objects.all().filter(hotel_id=pk)
        return Response({'types': room_type.values()} )
    

class RoomTypesViewSet(viewsets.ModelViewSet):
    queryset = Room_types.objects.all()
    serializer_class = RoomTypesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hotel', 'max_guests']
    
    
    @action(methods=['get'], detail=True)
    def rooms(self, request, pk=None):
        try:
            pk = Room_types.objects.get(pk=pk).id
        except Exception:
            return Response({'ОШИБКА': 'Такой комнаты не существует!'})
        room = Rooms.objects.all().filter(type_id=pk)
        return Response({'rooms': room.values()} )


class RoomsViewSet(viewsets.ModelViewSet):
    queryset = Rooms.objects.all()
    serializer_class = RoomsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hotel', 'type', 'is_available', 'floor']


class GuestsViewSet(viewsets.ModelViewSet):
    queryset = Guests.objects.all()
    serializer_class = GuestsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['first_name', 'last_name', 'email']
    

class BookingsViewSet(viewsets.ModelViewSet):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['guest', 'room', 'status']