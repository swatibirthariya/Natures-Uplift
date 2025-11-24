Natures Uplift - Django project (demo)

Path to this project on disk: /mnt/data/natures_uplift_full_django

How to run locally (VS Code):
1. Create virtualenv and install Django:
   python -m venv venv
   source venv/bin/activate   # (Windows: venv\Scripts\activate)
   pip install django
2. Run migrations:
   python manage.py migrate
3. Create superuser:
   python manage.py createsuperuser
4. Load sample plants (optional):
   python manage.py loaddata plants/initial_plants.json
5. Run server:
   python manage.py runserver
6. Open http://127.0.0.1:8000/

Notes:
- UPI ID displayed at checkout: 6366382516@ybl
- Delivery validation currently checks pincode starts with '56' (Bangalore). Provide full list to be strict.
- Payment flow is simulated. For production integrate PhonePe / Razorpay with server-side verification and HTTPS.
- Replace GSTIN placeholder in templates with your real GSTIN.
- Logo copied from uploaded file to static/images/logo.jpeg
