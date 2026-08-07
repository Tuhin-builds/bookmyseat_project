from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import URLValidator




class Movie(models.Model):
    name = models.CharField(max_length=255, db_index=True) 
    genre = models.CharField(max_length=100, db_index=True) 
    language = models.CharField(max_length=50, db_index=True) 
    release_date = models.DateField(db_index=True, null=True, blank=True) 
    image = models.URLField(max_length=500)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True) 
    trailer_url = models.URLField(max_length=500, blank=True, null=True, validators=[URLValidator()])

    class Meta:
        indexes = [
            models.Index(fields=['genre', 'language']),
            models.Index(fields=['release_date']),
        ]

    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='theaters')
    time= models.DateTimeField()

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater,on_delete=models.CASCADE,related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked=models.BooleanField(default=False)


    reserved_at = models.DateTimeField(null=True, blank=True)
    reserved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'
    
    

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, db_index=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, db_index=True)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, db_index=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    order_id = models.CharField(max_length=100, null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    status = models.CharField(max_length=20, default='PENDING', db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater.name}'