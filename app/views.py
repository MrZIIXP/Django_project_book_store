from django.shortcuts import render
from books.models import Book, Review, Author
from django.db.models import Avg, Count, FloatField
from django.db.models.functions import Coalesce


def home(request):
    stats = Book.objects.aggregate(
        total_books=Count('id'),
        avg_price=Avg('price'),
    )

    books = Book.objects.annotate(avg_rating=Coalesce(Avg(
        'review__rating'), 0.0, output_field=FloatField())).order_by('-avg_rating')[:3]
    avg_rating = Review.objects.aggregate(avg_rating=Coalesce(
        Avg('rating'), 0.0, output_field=FloatField()))

    authors = Author.objects.annotate(book_count=Count('books'))

    return render(request, 'home.html', {
        'stats': stats,
        'avg_rating': avg_rating if 'avg_rating' in avg_rating.keys() else {'avg_rating': 0},
        'authors': authors,
        'book_1': books[0] if len(books) > 0 else None,
        'book_2': books[1] if len(books) > 1 else None,
        'book_3': books[2] if len(books) > 2 else None,
    })
