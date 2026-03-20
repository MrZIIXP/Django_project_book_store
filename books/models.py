from django.db import models
from user.models import User


class Category(models.Model):
   name = models.CharField(unique=True, max_length=100)
   def __str__(self):
      return self.name

class Author(models.Model):
   full_name = models.CharField(max_length=100)
   bio = models.TextField(null=True, blank=True)
   def __str__(self):
      return self.full_name

class Book(models.Model):
   title = models.CharField(max_length=100)
   description = models.TextField()
   price = models.DecimalField(max_digits=10, decimal_places=2)
   image = models.ImageField(upload_to='books/')
   created_at = models.DateTimeField(auto_now_add=True)
   author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
   category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
   created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
   
   def __str__(self):
      return self.title

class Review(models.Model):
   book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='review')
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review')
   text = models.TextField(null=True, blank=True)
   rating = models.PositiveSmallIntegerField()
   created_at = models.DateTimeField(auto_now_add=True)
   
   def __str__(self):
      return self.text, self.rating