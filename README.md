Yes Madam API App 💇‍♀️💅
This repository contains the yes_madam_api Django application, which serves as the backend API for an on-demand home salon and wellness service like "Yes Madam." This app is designed to be integrated into a larger Django project, providing core functionalities for user management, service browsing, booking, and more.

Features Provided by This App:
User Authentication: Secure registration and login (phone-based custom user model).

Location Management: APIs for selecting cities and setting user-specific locations.

Service Browsing: Fetch categories and services within those categories.

Shopping Cart: Add services to a user's cart and view cart contents.

Booking Flow: Choose time slots, confirm bookings, and manage booking details.

Payment Integration: Initiate payments and check payment statuses.

Booking History: Retrieve a user's past and current bookings.

Review & Rating: Submit ratings and reviews for completed services.

Admin Capabilities: (Optional) Endpoints for basic management of services, users, and bookings.

Integration into a Django Project:
To use this yes_madam_api app, integrate it into your existing or a new Django project:

Place the App:
Copy the entire yes_madam_api folder into your Django project's root directory (the same directory where your manage.py file is located, alongside your main project folder, e.g., myproject/).

Your project structure should look like this:

your_django_project_root/
├── manage.py
├── myproject/          # Your main Django project folder (contains settings.py)
│   └── ...
└── yes_madam_api/      # This app's folder
    └── ...

Add to INSTALLED_APPS:
Open your project's settings.py file (e.g., myproject/settings.py) and add 'yes_madam_api', 'rest_framework', and 'rest_framework.authtoken' to your INSTALLED_APPS list:

# myproject/settings.py

INSTALLED_APPS = [
    # ... other Django default apps ...
    'rest_framework',
    'rest_framework.authtoken',
    'yes_madam_api', # Add your app here
]

# Crucial: Tell Django to use the custom User model from this app
AUTH_USER_MODEL = 'yes_madam_api.User'

Include App URLs:
Open your project's main urls.py file (e.g., myproject/urls.py) and include the URLs from yes_madam_api:

# myproject/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include all API endpoints from yes_madam_api under the '/api/' prefix
    path('api/', include('yes_madam_api.urls')),
]

Run Migrations:
Navigate to your project's root directory (where manage.py is) in your terminal and run the migrations. It's highly recommended to delete db.sqlite3 and the 00xx_*.py files in yes_madam_api/migrations/ (except __init__.py) before running these if this is a fresh integration, to avoid conflicts.

python manage.py makemigrations yes_madam_api
python manage.py migrate

Create a Superuser: (Optional, but recommended for admin access)

python manage.py createsuperuser

Run the Development Server:

python manage.py runserver

API Endpoints:
Once integrated and the server is running, all API endpoints will be accessible under the /api/ prefix (as configured in your project's urls.py).

User Onboarding:

POST /api/register/

POST /api/login/

Location Selection:

GET /api/cities/

POST /api/set-location/ (Requires authentication)

Browse Services:

GET /api/categories/

GET /api/categories/<int:category_id>/services/

Cart Management:

POST /api/cart/add/ (Requires authentication)

GET /api/cart/?user_id={user_id} (Requires authentication)

Booking Flow:

GET /api/timeslots/?service_id={service_id}&date={date} (Requires authentication)

POST /api/book/ (Requires authentication)

Payment Integration:

POST /api/payment/initiate/ (Requires authentication)

GET /api/payment/status/<str:booking_id>/ (Requires authentication)

Booking History:

GET /api/bookings/?user_id={user_id} (Requires authentication)

Review & Rating:

POST /api/rate/ (Requires authentication)

Admin APIs (Optional):

POST /api/admin/services/add/ (Requires authentication)

GET /api/admin/users/ (Requires authentication)

GET /api/admin/bookings/ (Requires authentication)

Technologies Used:
Django

Django REST Framework

Note: For detailed request/response formats and examples, refer to the API documentation that this app is based on.
