import logging
import time
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

def send_ticket_confirmation_email(booking_data, max_retries=3):
  
    subject = f"Booking Confirmation - {booking_data.get('movie_title')}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [booking_data.get('user_email')]

    html_content = render_to_string('emails/ticket_confirmation.html', booking_data)
    
    text_content = (
        f"Booking Confirmed!\n\n"
        f"Movie: {booking_data.get('movie_title')}\n"
        f"Theater: {booking_data.get('theater_name')}\n"
        f"Show Timing: {booking_data.get('show_time')}\n"
        f"Seat Numbers: {booking_data.get('seat_numbers')}\n"
        f"Payment ID: {booking_data.get('payment_id')}\n"
    )

    attempt = 0
    while attempt < max_retries:
        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            logger.info(f"Confirmation email successfully sent to {to_email} for Payment ID: {booking_data.get('payment_id')}")
            return True
        except Exception as e:
            attempt += 1
            logger.error(f"Attempt {attempt} failed to send email to {to_email}: {str(e)}")
            if attempt < max_retries:
                time.sleep(2)  # Wait 2 seconds before retrying
            else:
                logger.critical(f"All {max_retries} retry attempts failed for confirmation email to {to_email}.")
                return False