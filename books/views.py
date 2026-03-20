from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Book, Category, Author, Review
from user.models import User


def get_current_user(request):
    user_session = request.session.get('user')
    if not user_session:
        return None
    return get_object_or_404(User, id=user_session['id'])

def book_list(request):
    books = Book.objects.select_related('author', 'category').all()

    search = request.GET.get('search')
    category = request.GET.get('category')
    author = request.GET.get('author')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    exclude = request.GET.get('exclude')
    sort = request.GET.get('sort')

    if search:
        books = books.filter(title__icontains=search)

    if category:
        books = books.filter(category_id=category)

    if author:
        books = books.filter(author_id=author)

    if min_price:
        books = books.filter(price__gte=min_price)

    if max_price:
        books = books.filter(price__lte=max_price)

    if exclude:
        books = books.exclude(title__icontains=exclude)

    if sort:
        books = books.order_by(sort)

    categories = Category.objects.all()
    authors = Author.objects.all()

    return render(request, 'book_list.html', {
        'books': books,
        'categories': categories,
        'authors': authors
    })


def book_detail(request, pk):
    book = get_object_or_404(
        Book.objects.select_related(
            'author', 'category').prefetch_related('review'),
        id=pk
    )

    user = get_current_user(request)

    if request.method == 'POST' and user:
        if Review.objects.filter(book=book, user=user).exists():
            messages.error(request, "Вы уже оставили отзыв")
        else:
            rating = int(request.POST.get('rating'))
            text = request.POST.get('text')

            if 1 <= rating <= 5:
                Review.objects.create(
                    book=book,
                    user=user,
                    rating=rating,
                    text=text
                )
                messages.success(request, "Отзыв добавлен")
            else:
                messages.error(request, "Оценка должна быть от 1 до 5")

        return redirect('book_detail', pk=pk)

    return render(request, 'book_detail.html', {
        'book': book,
        'reviews': book.review.all()
    })


def book_create(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        Book.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            image=request.FILES.get('image'),
            author_id=request.POST.get('author'),
            category_id=request.POST.get('category'),
            created_by=user
        )
        messages.success(request, "Книга создана")
        return redirect('book_list')

    return render(request, 'book_create.html', {
        'authors': Author.objects.all(),
        'categories': Category.objects.all()
    })


# ✏️ UPDATE BOOK
def book_update(request, pk):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    book = get_object_or_404(Book, id=pk)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.description = request.POST.get('description')
        book.price = request.POST.get('price')
        book.author_id = request.POST.get('author')
        book.category_id = request.POST.get('category')

        if request.FILES.get('image'):
            book.image = request.FILES.get('image')

        book.save()
        messages.success(request, "Книга обновлена")
        return redirect('book_detail', pk=pk)

    return render(request, 'book_update.html', {
        'book': book,
        'authors': Author.objects.all(),
        'categories': Category.objects.all()
    })


# ❌ DELETE BOOK
def book_delete(request, pk):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    book = get_object_or_404(Book, id=pk)

    if request.method == 'POST':
        book.delete()
        messages.success(request, "Книга удалена")
        return redirect('book_list')

    return render(request, 'book_delete.html', {'book': book})


# ⭐ DELETE REVIEW
def review_delete(request, pk):
    user = get_current_user(request)
    review = get_object_or_404(Review, id=pk)

    if review.user != user:
        messages.error(request, "Нет доступа")
        return redirect('book_detail', pk=review.book.id)

    review.delete()
    messages.success(request, "Отзыв удален")
    return redirect('book_detail', pk=review.book.id)


def category_manage(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    # Создание или обновление
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name', '').strip()
        pk = request.POST.get('pk')

        if not name:
            messages.error(request, "Название обязательно")
            return redirect('category_manage')

        if action == 'create':
            Category.objects.create(name=name)
            messages.success(request, "Категория создана")
        elif action == 'update' and pk:
            category = get_object_or_404(Category, id=pk)
            category.name = name
            category.save()
            messages.success(request, "Категория обновлена")
        elif action == 'delete' and pk:
            category = get_object_or_404(Category, id=pk)
            category.delete()
            messages.success(request, "Категория удалена")

        return redirect('category_manage')

    # GET — показываем список
    categories = Category.objects.all()
    return render(request, 'category_manage.html', {'categories': categories})


def author_manage(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        action = request.POST.get('action')
        pk = request.POST.get('pk')
        full_name = request.POST.get('full_name', '').strip()
        bio = request.POST.get('bio', '').strip()

        if not full_name:
            messages.error(request, "Имя автора обязательно")
            return redirect('author_manage')

        if action == 'create':
            Author.objects.create(full_name=full_name, bio=bio)
            messages.success(request, "Автор создан")
        elif action == 'update' and pk:
            author = get_object_or_404(Author, id=pk)
            author.full_name = full_name
            author.bio = bio
            author.save()
            messages.success(request, "Автор обновлён")
        elif action == 'delete' and pk:
            author = get_object_or_404(Author, id=pk)
            author.delete()
            messages.success(request, "Автор удалён")

        return redirect('author_manage')

    authors = Author.objects.all()
    return render(request, 'author_manage.html', {'authors': authors})