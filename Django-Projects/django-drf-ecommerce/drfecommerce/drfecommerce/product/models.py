from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    # if we do wanna delete anything, we wanna delete all the child category first, before we delete any parent category
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ["name"]


    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_digital = models.BooleanField(default=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    # the product not necessary depend on the category so on_delete, would be SET_NULL
    category = TreeForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return self.name