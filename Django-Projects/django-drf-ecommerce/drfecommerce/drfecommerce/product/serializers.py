from rest_framework import serializers

from .models import Brand, Category, Product


# all the data will be serialized and returned to the frontend
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__" # what data we return to the client


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__" # what data we return to the client


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__" # what data we return to the client