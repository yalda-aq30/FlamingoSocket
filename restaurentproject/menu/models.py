from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', default='categories/default.jpg')     
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(null=True , blank=True , max_digits=7 , decimal_places=0)
    description = models.TextField(null=True , blank=True) 
    available = models.BooleanField(default=True)  
    category = models.ForeignKey(Category , on_delete=models.CASCADE , null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True) 

def __str__(self):
        return self.name