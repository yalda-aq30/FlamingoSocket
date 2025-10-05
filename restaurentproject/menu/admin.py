from django.contrib import admin
from .models import Product , Category
from django.utils.html import format_html
# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name' , 'price' , 'description' , 'available', 'image_tag') 


    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "-" 
    image_tag.short_description = 'Image' 


@admin.register(Category) 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  