import os
import django
import time
from datetime import timedelta
from django.utils import timezone
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Seat, Booking

def release_expired_seats():
    expiry_limit = timezone.now() - timedelta(minutes=2)
    
    
    all_booked = Seat.objects.filter(is_booked=True)
    
    if not all_booked.exists():
        return 

    
    print(f"[{timezone.localtime().strftime('%H:%M:%S')}] INFO: {all_booked.count()} active reservation(s) detected.")

    with transaction.atomic():
        expired_seats = Seat.objects.select_for_update().filter(
            is_booked=True, 
            reserved_at__lte=expiry_limit
        )
        
        if expired_seats.exists():
            count = expired_seats.count()
            print(f"[{timezone.localtime().strftime('%H:%M:%S')}] ! ACTION: Cleaning up {count} expired seat(s).")
            
            for seat in expired_seats:
                Booking.objects.filter(seat=seat).delete()
                seat.is_booked = False
                seat.reserved_at = None
                seat.reserved_by = None
                seat.save()
            
            print(f"[{timezone.localtime().strftime('%H:%M:%S')}] INFO: Cleanup complete. Database synchronized.")

print("--- Background cleanup service started ---")

while True:
    try:
        release_expired_seats()
    except Exception as e:
        print(f"[{timezone.localtime().strftime('%H:%M:%S')}] ERROR: {e}")
    
    time.sleep(10)