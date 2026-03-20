from django.urls import path
from .views import *

urlpatterns = [
    path('', book_list, name='book_list'),
    path('<int:pk>/', book_detail, name='book_detail'),

    path('create/', book_create, name='book_create'),
    path('<int:pk>/update/', book_update, name='book_update'),
    path('<int:pk>/delete/', book_delete, name='book_delete'),

    path('review/<int:pk>/delete/', review_delete, name='review_delete'),

    # Categories
    path('categories/manage/', category_manage, name='category_manage'),
    path('author/manage/', author_manage, name='author_manage'),
]