from django.shortcuts import render, redirect ,get_object_or_404
from .models import Movie,Theater,Seat,Booking
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from .models import Movie
import razorpay
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.shortcuts import render
from .models import Booking
from django.core.paginator import Paginator

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})


def movie_list(request):
    
    search_query = request.GET.get('search', '')
    selected_genres = request.GET.getlist('genre')
    selected_languages = request.GET.getlist('language')
    sort_by = request.GET.get('sort', '-release_date')
    page_number = request.GET.get('page', 1)

    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(name__icontains=search_query)

    if selected_genres:
        movies = movies.filter(genre__in=selected_genres)
    
    if selected_languages:
        movies = movies.filter(language__in=selected_languages)

    allowed_sorts = ['release_date', '-release_date', 'name', '-name', 'rating', '-rating']
    if sort_by in allowed_sorts:
        movies = movies.order_by(sort_by)

    genre_counts = Movie.objects.values('genre').annotate(count=Count('id'))
    language_counts = Movie.objects.values('language').annotate(count=Count('id'))

    paginator = Paginator(movies, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'movies': page_obj, 
        'search_query': search_query,
        'selected_genres': selected_genres,
        'selected_languages': selected_languages,
        'genre_counts': genre_counts,
        'language_counts': language_counts,
        'current_sort': sort_by,
    }
    return render(request, 'movies/movie_list.html', context)


def theater_list(request,movie_id):
    movie = get_object_or_404(Movie,id=movie_id)
    theater=Theater.objects.filter(movie=movie)
    return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater})



@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    
    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('seats')
        if not selected_seat_ids:
            return render(request, "movies/seat_selection.html", {'theaters': theater, "seats": Seat.objects.filter(theater=theater), 'error': "No seat selected"})
        
        try:
            with transaction.atomic():
                
                seats = Seat.objects.select_for_update().filter(id__in=selected_seat_ids, theater=theater)
                
               
                if seats.filter(is_booked=True).exists():

                   error_message = "The selected seats are no longer available."
                   return render(request, 'movies/seat_selection.html', {'theaters': theater, "seats": Seat.objects.filter(theater=theater), 'error': error_message})
                
                
                for seat in seats:
                    seat.is_booked = True
                    seat.reserved_at = timezone.now()
                    seat.reserved_by = request.user
                    seat.save()
                    
                    Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theater.movie,
                        theater=theater
                    )
            return redirect('profile')
            
        except IntegrityError:
            
            return render(request, 'movies/seat_selection.html', {'theaters': theater, "seats": Seat.objects.filter(theater=theater), 'error': "A booking error occurred. Please try again."})

    seats = Seat.objects.filter(theater=theater)
    return render(request, 'movies/seat_selection.html', {'theaters': theater, "seats": seats})

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def create_order(request):
    try:
        data = json.loads(request.body)
        seat_ids = data.get('seats', [])


        two_minutes_ago = timezone.now() - timedelta(minutes=2)
        Booking.objects.filter(status='PENDING', created_at__lt=two_minutes_ago).delete()


        for seat_id in seat_ids:
            if Booking.objects.filter(seat_id=seat_id, status='SUCCESS').exists():
                return JsonResponse({'error': 'Seat already booked'}, status=400)
            
            if Booking.objects.filter(seat_id=seat_id, status='PENDING').exists():
                return JsonResponse({'error': 'Seat is currently being processed'}, status=400)
        
        if not seat_ids:
            return JsonResponse({'error': 'No seats selected'}, status=400)

        amount = 500 * 100 * len(seat_ids)
        
        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": "order_rcptid_11",
            "payment_capture": 1
        })

        for seat_id in seat_ids:
            seat = Seat.objects.get(id=seat_id)
            Booking.objects.create(
                user=request.user,
                seat=seat,
                movie=seat.theater.movie,
                theater=seat.theater,
                order_id=order['id'],
                status='PENDING'
            )

        return JsonResponse({"order_id": order['id'], "key": settings.RAZORPAY_KEY_ID})

    except Exception as e:
        
        print(f"DEBUGGING ERROR: {e}") 
        
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def razorpay_webhook(request):
    print("Webhook received!")
    payload = request.body
    sig_header = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
    
    try:
        client.utility.verify_webhook_signature(payload, sig_header, settings.RAZORPAY_WEBHOOK_SECRET)
    except Exception:
        return HttpResponse('Invalid signature', status=400)

    data = json.loads(payload)
    
    if data['event'] == 'payment.captured':
        payment_entity = data['payload']['payment']['entity']
        order_id = payment_entity['order_id']
        payment_id = payment_entity['id']
        
        # Find ALL bookings associated with this order_id
        bookings = Booking.objects.filter(order_id=order_id, status='PENDING')
        
        for booking in bookings:
            booking.status = 'SUCCESS'
            booking.payment_id = payment_id
            booking.save()
            
            # Update seat availability
            seat = booking.seat
            seat.is_booked = True
            seat.save()
            
    return HttpResponse(status=200)



@staff_member_required
def admin_analytics(request):
   
    revenue = Booking.objects.filter(status='CONFIRMED').aggregate(Sum('price'))['price__sum'] or 0
    
    popular_movies = Booking.objects.values('movie__name').annotate(
        total_bookings=Count('id')
    ).order_by('-total_bookings')[:5]
    
    total = Booking.objects.count()
    cancelled = Booking.objects.filter(status='CANCELLED').count()
    cancellation_rate = (cancelled / total * 100) if total > 0 else 0
    
    context = {
        'revenue': revenue,
        'popular_movies': popular_movies,
        'cancellation_rate': round(cancellation_rate, 2),
    }
    return render(request, 'admin_analytics.html', context)