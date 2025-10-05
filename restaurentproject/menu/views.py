from django.shortcuts import render
from .models import Product , Category
# Create your views here.

def index(request):
    available_products = Product.objects.filter(available = True) 
    categories = Category.objects.all().order_by('-id')
    context = {
        'available_products' : available_products,
        'categories' : categories,
    }
    return render(request ,'menu/index.html' , context)   