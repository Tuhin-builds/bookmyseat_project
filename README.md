# Tech Stack & Environment
Python Version: 3.12.10
Django Version: 6.0.6




# Task 1: Secure YouTube Trailer Embedding
Objective: Implement secure, high-performance YouTube trailer embedding on movie detail pages with proper validation and fallback handling.


Implementation Highlights:

Security: Used URLField with URLValidator to prevent malicious data injection and avoided |safe in templates to mitigate XSS risks.

Performance: Implemented loading="lazy" on the iframe, verified via the Network tab to ensure media only loads when entering the viewport.

Robustness: Added {% if %} fallback logic to display a clear "Trailer currently unavailable" message when no valid URL is provided.






# Task 2: Concurrency-Safe Seat Reservation
Objective: Implement a seat booking system with row-level locking and automated timeout handling.


Implementation Highlights:

Concurrency: Utilized select_for_update() within transaction.atomic() to prevent double-booking during simultaneous requests.

Automated Cleanup: Created run_cleanup.py, a background service that independently monitors the database and releases reservations exceeding the 2-minute limit.

Resilience: System handles user abandonment and network interruptions by automatically resetting seat status and clearing orphaned booking records based on reservation timestamps.

Monitoring: Implemented event-driven terminal logging to provide real-time visibility into the system’s health and cleanup cycles.


Operation:
Start the background scheduler manually by running python run_cleanup.py in a separate terminal window.






# Task 3: Payment Gateway Integration with Idempotency and Webhook Security
Objective: Integrate Razorpay for ticket purchases with secure server-side verification, implementing idempotency and robust webhook handling to prevent double-booking.


Implementation Highlights:

Security: Performed server-side signature validation against secret keys to ensure payment authenticity and mitigated replay attacks.

Idempotency: Implemented transaction atomicity and event ID tracking to ensure each webhook event is processed exactly once, preventing duplicate transactions during retries.

Resilience: Designed system to gracefully handle timeouts and partial failures, ensuring consistent database state even during network interruptions.

Monitoring: Documented the complete payment lifecycle, from order creation to final fulfillment, to ensure transparency and ease of auditing.