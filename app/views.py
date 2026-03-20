from django.shortcuts import render
from books.models import Book, Review, Author
from django.db.models import Avg, Count


def home(request):
    stats = Book.objects.aggregate(
        total_books=Count('id'),
        avg_price=Avg('price'),
    )

    avg_rating = Review.objects.aggregate(avg_rating=Avg('rating'))

    authors = Author.objects.annotate(book_count=Count('books'))

    return render(request, 'home.html', {
        'stats': stats,
        'avg_rating': avg_rating if 'avg_rating' in avg_rating.keys() else {'avg_rating': 0},
        'authors': authors
    })
