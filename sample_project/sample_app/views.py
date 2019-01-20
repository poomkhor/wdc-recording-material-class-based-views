from datetime import datetime

from django.urls import reverse
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import View, TemplateView, RedirectView

from .models import Author, Book
from .forms import BookForm, SignUpForm


def is_staff(user):
    return user.is_staff

class IndexView(TemplateView):
    template_name = "books.html"

    def get_context_data(self, **kwargs):
        # Request data is now in `self.request`
        sort_method = self.request.GET.get('sort', 'asc')
        books = Book.objects.all()
        if sort_method == 'asc':
            books = books.order_by('popularity')
        elif sort_method == 'desc':
            books = books.order_by('-popularity')

        if 'q' in self.request.GET:
            q = self.request.GET['q']
            books = books.filter(title__icontains=q)

        # initialize list of favorite books for current session
        self.request.session.setdefault('favorite_books', [])
        self.request.session.save()

        return {
            'books': books,
            'authors': Author.objects.all(),
            'sort_method': sort_method,
        }

class BookDetailView(TemplateView):
    template_name = "book.html"
    def get_context_data(self, **kwargs):
        book = get_object_or_404(Book, id=kwargs['book_id'])
        return {'book': book}


class AuthorListView(TemplateView):
    template_name = "authors.html"
    def get_context_data(self, **kwargs):
        authors = Author.objects.all()
        return {
            'authors': authors
        }


class AuthorDetailView(TemplateView):
    template_name = "author.html"
    def get_context_data(self, **kwargs):
        author = get_object_or_404(Author, id=kwargs['author_id'])
        return {
            'author': author
        }


class AuthorByName(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        author = get_object_or_404(Author, name=kwargs['author_name'])
        return reverse('author_detail', args=[author.id])


# @login_required
# @user_passes_test(is_staff)
class CreateBookView(View):

    def get(self, request):
        book_form = BookForm()
        return render(
            request,
            'create_book.html',
            context={'book_form': book_form}
        )

    def post(self, request):
        book_form = BookForm(request.POST)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
        return render(
            request,
            'create_book.html',
            context={'book_form': book_form}
        )


@login_required
@user_passes_test(is_staff)
def edit_book(request, book_id=None):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'GET':
        book_form = BookForm(instance=book)
        return render(
            request,
            'edit_book.html',
            context={
                'book': book,
                'book_form': book_form
            }
        )
    elif request.method == 'POST':
        book_form = BookForm(request.POST, instance=book)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
        return render(
            request,
            'edit_book.html',
            context={
                'book': book,
                'book_form': book_form
            }
        )


@login_required
@user_passes_test(is_staff)
def delete_book(request):
    book_id = request.POST.get('book_id')
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('/')


def favorites(request):
    books_ids = request.session.get('favorite_books', [])
    favorite_books = Book.objects.filter(id__in=books_ids)
    return render(
        request,
        'favorites.html',
        context={
            'favorite_books': favorite_books,
        }
    )


def add_to_favorites(request):
    request.session.setdefault('favorite_books', [])
    request.session['favorite_books'].append(request.POST.get('book_id'))
    request.session.save()
    return redirect('index')


def remove_from_favorites(request):
    if request.session.get('favorite_books'):
        request.session['favorite_books'].remove(request.POST.get('book_id'))
        request.session.save()
    return redirect('index')


def signup(request):
    if request.method == 'GET':
        signup_form = SignUpForm()
        return render(
            request,
            'signup.html',
            context={'signup_form': signup_form}
        )
    elif request.method == 'POST':
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            user = User.objects.create(username=request.POST['username'])
            user.set_password(request.POST['password'])
            user.save()
            login(request, user)
            return redirect('index')
        return render(
            request,
            'signup.html',
            context={'signup_form': signup_form}
        )
