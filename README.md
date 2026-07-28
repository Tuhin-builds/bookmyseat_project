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






# Task 4: Advanced Admin Analytics Dashboard with Aggregation Optimization

Objective: Build a secure Admin Dashboard that displays real-time analytics including total revenue, most popular movies, busiest theaters, peak booking hours, and cancellation rates, optimized for large datasets.


Implementation Highlights:

Metrics: Real-time calculation of total revenue, popular movies based on bookings, seat occupancy rates, peak hours, and cancellation metrics.

Security: Implemented role-based authentication using decorators to restrict dashboard access to authorized staff and superusers, preventing privilege escalation and unauthorized API access.

Optimization: Utilized database-level aggregation functions (Sum, Count) instead of loading entire datasets into memory, paired with proper indexing for high performance on large datasets.

Caching: Configured in-memory caching mechanisms to prevent performance degradation under repeated queries or heavy traffic.






# Task 5: Scalable Genre and Language Filtering with Query Optimization

Objective: Implement advanced server-side multi-select filtering for genres and languages, optimized for large movie catalogs (5,000+ entries) with full index support, seamless pagination/sorting persistence, and dynamic reactive filter counts.


Implementation Highlights:

Multi-Select Filtering: Processed multiple selected genres and languages server-side using Django's `__in` queries to ensure flexible and accurate data retrieval.

Query Performance & Indexing: Configured single-field indexes (`db_index=True`) and a high-performance composite index (`models.Index(fields=['genre', 'language'])`) to completely prevent inefficient full-table scans.

Dynamic Filter Counts: Implemented independent base querysets with database-level aggregations (`.values().annotate(Count('id'))`) so that filter counts dynamically adjust based on active user constraints.

Pagination & Sorting Persistence: Preserved active search queries, filter combinations, and sorting attributes seamlessly across all pagination links.

Performance Justification: Leveraged database-side aggregation and strict indexing strategies to balance query flexibility with scalability, ensuring high performance even under large-scale movie catalogs.