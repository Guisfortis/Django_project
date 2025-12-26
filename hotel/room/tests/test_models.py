import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.db.utils import IntegrityError
from room.models import Hotels, Room_types, Rooms, Guests, Bookings


@pytest.mark.django_db
class TestHotelsModel:
    """Тесты модели Hotels"""
    
    def test_create_hotel_success(self):
        """Успешное создание отеля"""
        hotel = Hotels.objects.create(
            name='Test Hotel',
            address='Test Address',
            city='Test City',
            country='Test Country',
            phone='+12345678901',
            star_rating=4
        )
        
        assert hotel.pk is not None
        assert hotel.name == 'Test Hotel'
        assert hotel.city == 'Test City'
        assert hotel.star_rating == 4
        assert hotel.created_at is not None
        assert str(hotel) == 'Test Hotel'
    
    
    def test_hotel_required_fields(self):
        """Проверка обязательных полей"""
        with pytest.raises(IntegrityError):
            Hotels.objects.create(
                name='Test'  
            )
    

@pytest.mark.django_db
class TestRoomTypesModel:
    """Тесты модели Room_types"""
    def test_create_room_type(self, hotel):
        """Создание типа комнаты"""
        room_type = Room_types.objects.create(
            hotel=hotel,
            name='Presidential Suite',
            description='The most luxurious suite',
            base_price=Decimal('1000.00'),
            max_guests=2
        )
        
        assert room_type.hotel == hotel
        assert room_type.base_price == Decimal('1000.00')
        assert room_type.max_guests == 2
        assert str(room_type) == 'Presidential Suite'
    
    def test_room_type_default_price(self, hotel):
        """Проверка дефолтной цены"""
        room_type = Room_types.objects.create(
            hotel=hotel,
            name='Standard',
            description='Standard room',
            max_guests=1
        )
        assert room_type.base_price == Decimal('0.00')
    
    def test_room_type_price_precision(self, hotel):
        """Проверка точности цены"""
        room_type = Room_types.objects.create(
            hotel=hotel,
            name='Test',
            description='Test',
            base_price=Decimal('123.45'),
            max_guests=2
        )
        assert str(room_type.base_price) == '123.45'
    
    def test_room_type_hotel_cascade(self, hotel):
        """Проверка каскадного удаления отеля"""
        room_type = Room_types.objects.create(
            hotel=hotel,
            name='Test Type',
            description='Test',
            max_guests=2
        )
        hotel_id = hotel.id
        hotel.delete()
        assert not Room_types.objects.filter(id=room_type.id).exists()
        assert not Hotels.objects.filter(id=hotel_id).exists()


@pytest.mark.django_db
class TestRoomsModel:
    """Тесты модели Rooms"""
    def test_create_room(self, hotel, room_type):
        """Создание комнаты"""
        room = Rooms.objects.create(
            hotel=hotel,
            type=room_type,
            room_number='501',
            floor=5,
            is_available=True
        )
        
        assert room.room_number == '501'
        assert room.floor == 5
        assert room.is_available is True
        assert room.hotel == hotel
        assert room.type == room_type
        assert str(room) == '501'
    
    def test_room_default_availability(self, hotel, room_type):
        """Дефолтное значение is_available"""
        room = Rooms.objects.create(
            hotel=hotel,
            type=room_type,
            room_number='502',
            floor=5
        )
        assert room.is_available is True
    
    
    def test_room_cascade_deletions(self, hotel, room_type):
        """Каскадное удаление при удалении отеля и типа"""
        room = Rooms.objects.create(
            hotel=hotel,
            type=room_type,
            room_number='601',
            floor=6
        )

        hotel.delete()
        assert not Rooms.objects.filter(id=room.id).exists()


@pytest.mark.django_db
class TestGuestsModel:
    """Тесты модели Guests"""
    
    def test_create_guest(self):
        """Создание гостя"""
        guest = Guests.objects.create(
            first_name='Anna',
            last_name='Petrova',
            email='anna.petrova@example.com',
            phone='+79991234567',
            passport='RU1234567'
        )
        
        assert guest.first_name == 'Anna'
        assert guest.last_name == 'Petrova'
        assert guest.email == 'anna.petrova@example.com'
        assert guest.passport == 'RU1234567'
        assert guest.registration_date is not None
        assert str(guest) == 'Anna Petrova'
    
    
    def test_guest_auto_registration_date(self):
        """Автоматическая установка даты регистрации"""
        import time
        time.sleep(0.1)
        
        guest = Guests.objects.create(
            first_name='Test',
            last_name='Test',
            email='test@test.com',
            phone='+70000000000',
            passport='TEST0001'
        )
        
        assert guest.registration_date is not None



@pytest.mark.django_db
class TestBookingsModel:
    """Тесты модели Bookings"""
    
    def test_create_booking(self, guest, room):
        """Создание бронирования"""
        check_in = date.today() + timedelta(days=10)
        check_out = check_in + timedelta(days=7)
        
        booking = Bookings.objects.create(
            guest=guest,
            room=room,
            check_in_date=check_in,
            check_out_date=check_out,
            total_price=Decimal('2100.00'),
            status='confirmed'
        )
        
        assert booking.guest == guest
        assert booking.room == room
        assert booking.check_in_date == check_in
        assert booking.check_out_date == check_out
        assert booking.total_price == Decimal('2100.00')
        assert booking.status == 'confirmed'
        assert booking.created_at is not None
        assert str(booking) == f"Booking {guest}"
    
    def test_booking_default_price(self, guest, room):
        """Дефолтная цена бронирования"""
        booking = Bookings.objects.create(
            guest=guest,
            room=room,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
            status='pending'
        )
        assert booking.total_price == Decimal('0.00')
    
    
    def test_booking_relationships(self, booking):
        """Связи бронирования c гостем и комнатой"""
        
        assert booking.guest is not None
        assert booking.room is not None
        
        
        assert booking in booking.guest.bookings_set.all()
        assert booking in booking.room.bookings_set.all()


@pytest.mark.django_db
class TestModelRelationships:
    """Тесты связей между моделями"""
    
    def test_hotel_room_types_relationship(self, hotel):
        """Связь один-ко-многим: Отель -> Типы комнат"""
        
        types_data = [
            ('Standard', Decimal('100.00'), 2),
            ('Deluxe', Decimal('200.00'), 3),
            ('Suite', Decimal('350.00'), 4)
        ]
        
        for name, price, guests in types_data:
            Room_types.objects.create(
                hotel=hotel,
                name=name,
                description=f'{name} room',
                base_price=price,
                max_guests=guests
            )
        
        
        hotel_room_types = hotel.room_types_set.all()
        assert hotel_room_types.count() == 3
        assert all(rt.hotel == hotel for rt in hotel_room_types)
    
    def test_room_type_rooms_relationship(self, room_type):
        """Связь один-ко-многим: Тип комнаты -> Комнаты"""
        
        rooms_data = [
            ('101', 1, True),
            ('102', 1, True),
            ('103', 1, False)
        ]
        
        for number, floor, available in rooms_data:
            Rooms.objects.create(
                hotel=room_type.hotel,
                type=room_type,
                room_number=number,
                floor=floor,
                is_available=available
            )
        
        
        type_rooms = room_type.rooms_set.all()
        assert type_rooms.count() == 3
        assert all(r.type == room_type for r in type_rooms)
