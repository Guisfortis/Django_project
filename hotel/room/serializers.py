from rest_framework import serializers
from .models import Hotels, Rooms, Room_types, Bookings, Guests


class HotelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotels
        fields = '__all__'

class RoomTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room_types
        fields = '__all__'
        

class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields ='__all__'


class GuestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guests
        fields ='__all__'


class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields ='__all__'