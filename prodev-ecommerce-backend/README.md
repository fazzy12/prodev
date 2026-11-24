# ProDev E-Commerce Backend API

A scalable, production-ready RESTful backend for an e-commerce product catalog built with **Django**, **Django REST Framework**, **PostgreSQL**, **JWT Authentication**, and **OpenAPI/Swagger**.

---

## Live Deployment

* **Live API Base URL:** [https://prodev-ecommerce-backend.onrender.com/](https://prodev-ecommerce-backend.onrender.com/)
* **Interactive Swagger Documentation:** [https://prodev-ecommerce-backend.onrender.com/api/docs/](https://prodev-ecommerce-backend.onrender.com/api/docs/)
* **OpenAPI Schema:** [https://prodev-ecommerce-backend.onrender.com/api/schema/](https://prodev-ecommerce-backend.onrender.com/api/schema/)

*(Note: Hosted on Render's free tier; the first request after 15 minutes of inactivity may take ~30–50 seconds while the server wakes up.)*

---

## Key Features

* **JWT Authentication & Role-Based Access Control:** Secure user registration, login, token refresh, and profile retrieval using `djangorestframework-simplejwt`, with custom `IsAdminOrReadOnly` permissions separating public catalog browsing from admin catalog management.
* **Catalog CRUD Operations:** Full Create, Read, Update, and Delete endpoints for categories and products using slug-based lookups.
* **Advanced Querying:** Built-in filtering by category slug, price range (`min_price`, `max_price`), and stock availability (`in_stock`), combined with full-text search, multi-field sorting (`price`, `created_at`, `name`), and paginated responses.
* **Database Optimization:** Strategic PostgreSQL B-tree single and composite indexes on high-traffic query fields (`price`, `(category, price)`, `(is_active, -created_at)`) and `select_related` query optimization to eliminate N+1 query bottlenecks.
* **Interactive API Documentation:** Auto-generated OpenAPI 3.0 schema and interactive Swagger UI powered by `drf-spectacular`.

---

## Tech Stack

* **Backend Framework:** Python 3.12+, Django, Django REST Framework
* **Database:** PostgreSQL
* **Authentication:** SimpleJWT (Bearer Token)
* **Filtering & Search:** `django-filter`, DRF `SearchFilter` & `OrderingFilter`
* **Documentation:** `drf-spectacular` (Swagger UI)
* **Deployment & Static Serving:** Render, Gunicorn, WhiteNoise

---

## Project Structure

```text
prodev-ecommerce-backend/
├── apps/
│   ├── catalog/          # Category & Product models, filters, permissions, CRUD views, tests
│   └── users/            # Custom UUID User model, JWT auth & profile endpoints
├── config/               # Django settings, root URL routing, WSGI/ASGI entrypoints
├── build.sh              # Render build & migration script
├── manage.py
├── Procfile              # Production Gunicorn process definition
├── requirements.txt
└── README.md
```

---

## Local Setup & Installation

### 1. Clone the Repository & Create Virtual Environment
```bash
git clone https://github.com/fazzy12/prodev.git
cd prodev/prodev-ecommerce-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure PostgreSQL
Create a local PostgreSQL database and user:
```sql
CREATE DATABASE ecommerce_db;
CREATE USER ecommerce_user WITH PASSWORD 'strongpassword123';
ALTER DATABASE ecommerce_db OWNER TO ecommerce_user;
ALTER USER ecommerce_user CREATEDB;
```

### 3. Set Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-super-secret-django-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=strongpassword123
DB_HOST=localhost
DB_PORT=5432
```

### 4. Apply Migrations & Create Admin User
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

---

## Running Automated Tests

Run the test suite (verifies public filtering/sorting, JWT role permissions, and constant query count via `assertNumQueries`):
```bash
python manage.py test
```

---

## API Endpoints Reference

### Authentication (`/api/auth/`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Public | Register a new customer account |
| `POST` | `/api/auth/login/` | Public | Obtain JWT `access` and `refresh` tokens |
| `POST` | `/api/auth/token/refresh/` | Public | Refresh an expired access token |
| `GET` | `/api/auth/me/` | Authenticated | Retrieve current user profile |
| `PATCH` | `/api/auth/me/` | Authenticated | Update current user profile |

### Categories (`/api/categories/`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/categories/` | Public | List all categories |
| `POST` | `/api/categories/` | Admin | Create a new category |
| `GET` | `/api/categories/{slug}/` | Public | Retrieve category details |
| `PATCH` | `/api/categories/{slug}/` | Admin | Update a category |
| `DELETE` | `/api/categories/{slug}/` | Admin | Delete a category |

### Products (`/api/products/`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/products/` | Public | List products with filtering, search, sorting & pagination |
| `POST` | `/api/products/` | Admin | Create a new product |
| `GET` | `/api/products/{slug}/` | Public | Retrieve product details |
| `PATCH` | `/api/products/{slug}/` | Admin | Update a product |
| `DELETE` | `/api/products/{slug}/` | Admin | Delete a product |

#### Supported Product Query Parameters
* **Filter by category slug:** `?category=electronics`
* **Filter by price range:** `?min_price=20&max_price=500`
* **Filter by stock availability:** `?in_stock=true`
* **Search by name/description:** `?search=keyboard`
* **Sort results:** `?ordering=price`, `?ordering=-price`, or `?ordering=-created_at`
* **Pagination:** `?page=2`

---

## Testing Protected Endpoints in Swagger UI

1. Open [https://prodev-ecommerce-backend.onrender.com/api/docs/](https://prodev-ecommerce-backend.onrender.com/api/docs/).
2. Execute `POST /api/auth/login/` with your admin credentials and copy the returned `access` token.
3. Click the **Authorize** button at the top right of the Swagger UI.
4. Paste your token into the `BearerAuth` value box and click **Authorize**.
5. You can now execute `POST`, `PATCH`, and `DELETE` requests on categories and products directly from your browser.