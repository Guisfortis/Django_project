from django.forms import ValidationError
import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from room.models import Hotels, Room_types, Rooms, Guests, Bookings


@pytest.mark.django_db
class TestHotelsViewSet:
    """Тесты для HotelsViewSet"""
    
    def test_list_hotels(self, api_client, hotel, hotel_with_low_rating):
        """GET /api/v1/hotels/ - список отелей"""
        url = reverse('hotel-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        
        hotel_data = next((h for h in response.data if h['id'] == hotel.id), None)
        assert hotel_data is not None
        assert hotel_data['name'] == hotel.name
        assert hotel_data['star_rating'] == hotel.star_rating
    
    def test_retrieve_hotel(self, api_client, hotel):
        """GET /api/v1/hotels/{id}/ - получение конкретного отеля"""
        url = reverse('hotel-detail', kwargs={'pk': hotel.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == hotel.id
        assert response.data['name'] == hotel.name
        assert response.data['city'] == hotel.city
        assert response.data['country'] == hotel.country
    
    def test_create_hotel(self, api_client, hotel_data):
        """POST /api/v1/hotels/ - создание отеля"""
        url = reverse('hotel-list')
        response = api_client.post(url, hotel_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == hotel_data['name']
        assert Hotels.objects.filter(name=hotel_data['name']).exists()
    
    def test_update_hotel(self, api_client, hotel):
        """PATCH /api/v1/hotels/{id}/ - обновление отеля"""
        url = reverse('hotel-detail', kwargs={'pk': hotel.pk})
        update_data = {'name': 'Updated Hotel Name', 'star_rating': 4}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        hotel.refresh_from_db()
        assert hotel.name == 'Updated Hotel Name'
        assert hotel.star_rating == 4
    
    def test_delete_hotel(self, api_client, hotel):
        """DELETE /api/v1/hotels/{id}/ - удаление отеля (без аутентификации)"""
        url = reverse('hotel-detail', kwargs={'pk': hotel.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Hotels.objects.filter(pk=hotel.pk).exists()
    
    def test_hotel_room_types_action(self, api_client, hotel, room_type, economy_room_type):
        """GET /api/v1/hotels/{id}/room_types/"""
        url = reverse('hotel-room-types', kwargs={'pk': hotel.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'types' in response.data
        assert len(response.data['types']) == 2
        
        type_ids = [rt['id'] for rt in response.data['types']]
        assert room_type.id in type_ids
        assert economy_room_type.id in type_ids
    
    def test_hotel_room_types_action_invalid_hotel(self, api_client):
        """Кастомное действие c несуществующим отелем"""
        url = reverse('hotel-room-types', kwargs={'pk': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'ОШИБКА' in response.data
        assert response.data['ОШИБКА'] == 'Такого отеля не существует!'
    
    def test_hotel_filter_by_country(self, api_client, hotel, hotel_with_low_rating):
        """Фильтрация отелей по стране"""
        url = reverse('hotel-list')
        
        response = api_client.get(url, {'country': hotel.country})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_hotel_filter_by_star_rating(self, api_client, hotel, hotel_with_low_rating):
        """Фильтрация отелей по звездному рейтингу"""
        url = reverse('hotel-list')
        
        response = api_client.get(url, {'star_rating': 5})
        assert response.status_code == status.HTTP_200_OK


        hotel_ids = [h['id'] for h in response.data]
        assert hotel.id in hotel_ids
        assert hotel_with_low_rating.id not in hotel_ids
    
    def test_create_hotel_invalid_data(self, api_client):
        """Создание отеля с некорректными данными"""
        url = reverse('hotel-list')
        invalid_data = {
            'name': '',  
            'address': 'Test',
            'city': 'Test',
            'country': 'Test',
            'phone': 'invalid_phone',  
            'star_rating': 10
        }
        response = api_client.post(url, invalid_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data or 'phone' in response.data or 'star_rating' in response.data


@pytest.mark.django_db
class TestRoomTypesViewSet:
    """Тесты для RoomTypesViewSet"""
    
    def test_list_room_types(self, api_client, room_type, economy_room_type):
        """GET /api/v1/room_types/ - список типов комнат"""
        url = reverse('room_types-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
    
    def test_retrieve_room_type(self, api_client, room_type):
        """GET /api/v1/room_types/{id}/ - получение конкретного типа"""
        url = reverse('room_types-detail', kwargs={'pk': room_type.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == room_type.id
        assert response.data['name'] == room_type.name
        assert response.data['base_price'] == str(room_type.base_price)
    
    def test_create_room_type(self, api_client, hotel, room_type_data):
        """POST /api/v1/room_types/ - создание типа комнаты"""
        url = reverse('room_types-list')
        response = api_client.post(url, room_type_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == room_type_data['name']
        assert response.data['hotel'] == hotel.id
        assert Room_types.objects.filter(name=room_type_data['name']).exists()
    
    def test_update_room_type(self, api_client, room_type):
        """PATCH /api/v1/room_types/{id}/ - обновление типа комнаты"""
        url = reverse('room_types-detail', kwargs={'pk': room_type.pk})
        update_data = {'name': 'Updated Room Type', 'base_price': '300.00'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        room_type.refresh_from_db()
        assert room_type.name == 'Updated Room Type'
        assert room_type.base_price == Decimal('300.00')
    
    def test_delete_room_type(self, api_client, room_type):
        """DELETE /api/v1/room_types/{id}/ - удаление типа комнаты"""
        url = reverse('room_types-detail', kwargs={'pk': room_type.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Room_types.objects.filter(pk=room_type.pk).exists()
    
    def test_room_types_rooms_action(self, api_client, room_type, room, unavailable_room):
        """GET /api/v1/room_types/{id}/rooms/"""
        url = reverse('room_types-rooms', kwargs={'pk': room_type.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'rooms' in response.data
        assert len(response.data['rooms']) == 2
        
        room_numbers = [r['room_number'] for r in response.data['rooms']]
        assert room.room_number in room_numbers
        assert unavailable_room.room_number in room_numbers
    
    def test_room_types_rooms_action_invalid_type(self, api_client):
        """Кастомное действие c несуществующим типом"""
        url = reverse('room_types-rooms', kwargs={'pk': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'ОШИБКА' in response.data
        assert response.data['ОШИБКА'] == 'Такой комнаты не существует!'
    
    def test_room_types_filter_by_hotel(self, api_client, hotel, room_type, economy_room_type):
        """Фильтрация типов комнат по отелю"""
        url = reverse('room_types-list')
        
        response = api_client.get(url, {'hotel': hotel.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        
        type_ids = [rt['id'] for rt in response.data]
        assert room_type.id in type_ids
        assert economy_room_type.id in type_ids


@pytest.mark.django_db
class TestRoomsViewSet:
    """Тесты для RoomsViewSet"""
    
    def test_list_rooms(self, api_client, room, unavailable_room):
        """GET /api/v1/rooms/ - список комнат"""
        url = reverse('rooms-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
    
    def test_retrieve_room(self, api_client, room):
        """GET /api/v1/rooms/{id}/ - получение конкретной комнаты"""
        url = reverse('rooms-detail', kwargs={'pk': room.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == room.id
        assert response.data['room_number'] == room.room_number
        assert response.data['is_available'] == room.is_available
    
    def test_create_room(self, api_client, hotel, room_type, room_data):
        """POST /api/v1/rooms/ - создание комнаты"""
        url = reverse('rooms-list')
        response = api_client.post(url, room_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['room_number'] == room_data['room_number']
        assert response.data['hotel'] == hotel.id
        assert response.data['type'] == room_type.id
        assert Rooms.objects.filter(room_number=room_data['room_number']).exists()
    
    def test_update_room(self, api_client, room):
        """PATCH /api/v1/rooms/{id}/ - обновление комнаты"""
        url = reverse('rooms-detail', kwargs={'pk': room.pk})
        update_data = {'is_available': False, 'room_number': '999'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        room.refresh_from_db()
        assert room.is_available is False
        assert room.room_number == '999'
    
    def test_delete_room(self, api_client, room):
        """DELETE /api/v1/rooms/{id}/ - удаление комнаты"""
        url = reverse('rooms-detail', kwargs={'pk': room.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Rooms.objects.filter(pk=room.pk).exists()
    
    def test_filter_rooms_by_availability(self, api_client, room, unavailable_room):
        """Фильтрация комнат по доступности"""
        url = reverse('rooms-list')
        
        response = api_client.get(url, {'is_available': 'true'})
        assert response.status_code == status.HTTP_200_OK
        
        available_rooms = [r for r in response.data if r['is_available']]
        assert len(available_rooms) >= 1
        assert any(r['id'] == room.id for r in available_rooms)
        assert not any(r['id'] == unavailable_room.id for r in available_rooms)
    
    def test_filter_rooms_by_hotel(self, api_client, hotel, room, unavailable_room):
        """Фильтрация комнат по отелю"""
        url = reverse('rooms-list')
        
        response = api_client.get(url, {'hotel': hotel.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        
        room_ids = [r['id'] for r in response.data]
        assert room.id in room_ids
        assert unavailable_room.id in room_ids


@pytest.mark.django_db
class TestGuestsViewSet:
    """Тесты для GuestsViewSet"""
    
    def test_list_guests(self, api_client, guest, another_guest):
        """GET /api/v1/guests/ - список гостей"""
        url = reverse('guests-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
    
    def test_retrieve_guest(self, api_client, guest):
        """GET /api/v1/guests/{id}/ - получение конкретного гостя"""
        url = reverse('guests-detail', kwargs={'pk': guest.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == guest.id
        assert response.data['first_name'] == guest.first_name
        assert response.data['last_name'] == guest.last_name
        assert response.data['email'] == guest.email
    
    def test_create_guest(self, api_client, guest_data):
        """POST /api/v1/guests/ - создание гостя"""
        url = reverse('guests-list')
        response = api_client.post(url, guest_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['first_name'] == guest_data['first_name']
        assert response.data['last_name'] == guest_data['last_name']
        assert response.data['email'] == guest_data['email']
        assert Guests.objects.filter(email=guest_data['email']).exists()
    
    def test_update_guest(self, api_client, guest):
        """PATCH /api/v1/guests/{id}/ - обновление гостя"""
        url = reverse('guests-detail', kwargs={'pk': guest.pk})
        update_data = {'first_name': 'UpdatedName', 'phone': '+79998887766'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        guest.refresh_from_db()
        assert guest.first_name == 'UpdatedName'
        assert str(guest.phone) == '+79998887766'
    
    def test_delete_guest(self, api_client, guest):
        """DELETE /api/v1/guests/{id}/ - удаление гостя"""
        url = reverse('guests-detail', kwargs={'pk': guest.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Guests.objects.filter(pk=guest.pk).exists()
    
    def test_search_guests_by_name(self, api_client, guest):
        """Поиск гостей по имени"""
        url = reverse('guests-list')
        
        response = api_client.get(url, {'first_name': guest.first_name})
        assert response.status_code == status.HTTP_200_OK
        assert any(g['id'] == guest.id for g in response.data)
        
        response = api_client.get(url, {'last_name': guest.last_name})
        assert response.status_code == status.HTTP_200_OK
        assert any(g['id'] == guest.id for g in response.data)
    



@pytest.mark.django_db
class TestBookingsViewSet:
    """Тесты для BookingsViewSet"""
    
    def test_list_bookings(self, api_client, booking):
        """GET /api/v1/bookings/ - список бронирований"""
        url = reverse('bookings-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_retrieve_booking(self, api_client, booking):
        """GET /api/v1/bookings/{id}/ - получение конкретного бронирования"""
        url = reverse('bookings-detail', kwargs={'pk': booking.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == booking.id
        assert response.data['guest'] == booking.guest.id
        assert response.data['room'] == booking.room.id
        assert response.data['status'] == booking.status
    
    def test_create_booking(self, api_client, guest, room, booking_data):
        """POST /api/v1/bookings/ - создание бронирования"""
        url = reverse('bookings-list')
        response = api_client.post(url, booking_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['guest'] == guest.id
        assert response.data['room'] == room.id
        assert response.data['status'] == booking_data['status']
        
        new_booking = Bookings.objects.filter(
            guest=guest,
            room=room,
            status='pending'
        ).first()
        assert new_booking is not None
    
    def test_update_booking(self, api_client, booking):
        """PATCH /api/v1/bookings/{id}/ - обновление бронирования"""
        url = reverse('bookings-detail', kwargs={'pk': booking.pk})
        update_data = {'status': 'cancelled', 'total_price': '1000.00'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == 'cancelled'
        assert booking.total_price == Decimal('1000.00')
    
    def test_delete_booking(self, api_client, booking):
        """DELETE /api/v1/bookings/{id}/ - удаление бронирования"""
        url = reverse('bookings-detail', kwargs={'pk': booking.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Bookings.objects.filter(pk=booking.pk).exists()
    
    def test_filter_bookings_by_status(self, api_client, booking):
        """Фильтрация бронирований по статусу"""
        url = reverse('bookings-list')
        
        response = api_client.get(url, {'status': 'confirmed'})
        assert response.status_code == status.HTTP_200_OK
        
        confirmed_bookings = [b for b in response.data]
        assert len(confirmed_bookings) >= 1
        assert any(b['id'] == booking.id for b in confirmed_bookings)
    
    def test_create_booking_invalid_dates(self, api_client, invalid_booking_data):
        """Создание бронирования c некорректными датами"""
        url = reverse('bookings-list')
        with pytest.raises(ValidationError):
            api_client.post(url, invalid_booking_data, format='json')
        
    
    
    def test_create_booking_past_date(self, api_client, guest, room):
        """Создание бронирования на прошедшую дату"""
        url = reverse('bookings-list')
        past_date_data = {
            'guest': guest.id,
            'room': room.id,
            'check_in_date': (date.today() - timedelta(days=10)).isoformat(),
            'check_out_date': (date.today() - timedelta(days=5)).isoformat(),
            'total_price': '500.00',
            'status': 'confirmed'
        }
        with pytest.raises(ValidationError):
            api_client.post(url, past_date_data, format='json')
        
            