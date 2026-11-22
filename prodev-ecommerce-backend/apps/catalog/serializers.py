from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('slug',)

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = ('id', 'category', 'category_name', 'name', 'slug', 'description', 'price', 'stock_quantity', 'is_active', 'created_at')
        read_only_fields = ('slug', 'created_at')
