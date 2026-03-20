from django.contrib import admin
from .models import Author, Book, Category, Review


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
   list_display = ['full_name']
   search_fields = ['full_name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
   list_display = ['name']
   search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
   list_display = ['title', 'price', 'created_at', 'created_by']
   list_filter = ['category', 'author']
   search_fields = ['category', 'author', 'title']

admin.site.register(Review)