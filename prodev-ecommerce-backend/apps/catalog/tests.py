from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category, Product

User = get_user_model()


class CatalogAPITests(APITestCase):
    def setUp(self):
        # 1. Create regular and admin users
        self.regular_user = User.objects.create_user(
            email="customer@example.com",
            username="customer",
            password="strongpassword123",
            is_admin=False,
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            username="adminuser",
            password="strongpassword123",
            is_admin=True,
        )

        # 2. Generate JWT access tokens
        self.regular_token = str(RefreshToken.for_user(self.regular_user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)

        # 3. Create categories
        self.electronics = Category.objects.create(
            name="Electronics", description="Gadgets and devices"
        )
        self.clothing = Category.objects.create(
            name="Clothing", description="Apparel and accessories"
        )

        # 4. Create initial products across different prices and categories
        self.product_cheap = Product.objects.create(
            category=self.clothing,
            name="Basic T-Shirt",
            description="Cotton crew neck tee",
            price=Decimal("8.00"),
            stock_quantity=50,
            is_active=True,
        )
        self.product_mid = Product.objects.create(
            category=self.electronics,
            name="Wireless Mouse",
            description="Ergonomic optical mouse",
            price=Decimal("25.00"),
            stock_quantity=20,
            is_active=True,
        )
        self.product_expensive = Product.objects.create(
            category=self.electronics,
            name="Mechanical Keyboard",
            description="RGB backlit mechanical keyboard",
            price=Decimal("120.00"),
            stock_quantity=10,
            is_active=True,
        )

        # URLs generated via DRF DefaultRouter basenames
        self.product_list_url = reverse("product-list")
        self.category_list_url = reverse("category-list")

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ------------------------------------------------------------------
    # 1. Public Read, Filtering, Sorting & Pagination Tests
    # ------------------------------------------------------------------

    def test_unauthenticated_user_can_list_filter_and_sort_products(self):
        """
        Verify unauthenticated GET requests work with min_price filtering and price ordering.
        """
        response = self.client.get(
            self.product_list_url, {"min_price": 10, "ordering": "price"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure pagination structure exists
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)

        results = response.data["results"]
        # Should exclude the $8.00 T-Shirt and sort ascending ($25.00 then $120.00)
        self.assertEqual(results[0]["name"], "Wireless Mouse")
        self.assertEqual(results[1]["name"], "Mechanical Keyboard")

    def test_filter_products_by_category_slug(self):
        """
        Verify filtering by category slug returns only products in that category.
        """
        response = self.client.get(
            self.product_list_url, {"category": "electronics"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        for item in response.data["results"]:
            self.assertEqual(item["category_name"], "Electronics")

    # ------------------------------------------------------------------
    # 2. Role-Based Permission Tests (JWT)
    # ------------------------------------------------------------------

    def test_unauthenticated_user_cannot_create_product(self):
        """
        Verify unauthenticated POST requests are rejected with 401 Unauthorized.
        """
        payload = {
            "category": str(self.electronics.id),
            "name": "USB-C Hub",
            "description": "Multi-port adapter",
            "price": "35.00",
            "stock_quantity": 15,
        }
        response = self.client.post(self.product_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_gets_403_when_creating_product(self):
        """
        Verify authenticated non-admin users receive 403 Forbidden on POST.
        """
        self.authenticate(self.regular_token)
        payload = {
            "category": str(self.electronics.id),
            "name": "USB-C Hub",
            "description": "Multi-port adapter",
            "price": "35.00",
            "stock_quantity": 15,
        }
        response = self.client.post(self.product_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_with_jwt_gets_201_created(self):
        """
        Verify authenticated admin users can create a product and receive 201 Created.
        """
        self.authenticate(self.admin_token)
        payload = {
            "category": str(self.electronics.id),
            "name": "Noise Cancelling Headphones",
            "description": "Over-ear wireless headphones",
            "price": "199.99",
            "stock_quantity": 12,
            "is_active": True,
        }
        response = self.client.post(self.product_list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Noise Cancelling Headphones")
        self.assertEqual(response.data["slug"], "noise-cancelling-headphones")
        self.assertEqual(Product.objects.count(), 4)

    # ------------------------------------------------------------------
    # 3. Query Optimization Test (N+1 Prevention)
    # ------------------------------------------------------------------

    def test_product_list_query_count_remains_constant(self):
        """
        Verify select_related('category') keeps query count at 2
        (1 for pagination COUNT(*), 1 for JOINed product+category rows)
        even after adding more products.
        """
        # Bulk-create 7 more products (total 10, fitting on page 1)
        extra_products = [
            Product(
                category=self.electronics if i % 2 == 0 else self.clothing,
                name=f"Bulk Item {i}",
                slug=f"bulk-item-{i}",
                description="Sample description",
                price=Decimal("50.00"),
                stock_quantity=10,
                is_active=True,
            )
            for i in range(7)
        ]
        Product.objects.bulk_create(extra_products)

        with self.assertNumQueries(2):
            response = self.client.get(self.product_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 10)