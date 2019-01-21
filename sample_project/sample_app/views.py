from datetime import datetime

from django.urls import reverse
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import View, TemplateView, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

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


class AuthorListView(ListView):
    model = Author
    # paginate_by = 3


class AuthorDetailView(DetailView):
    model = Author

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['now'] = timezone.now()
    #     return context


class BookDetailView(DetailView):
    model = Book


class CreateBookView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'create_book.html'
    success_url = '/'

    model = Book
    fields = ['title', 'author', 'isbn', 'popularity']

    def test_func(self):
        return is_staff(self.request.user)


class BookUpdateView(UpdateView):
    template_name = 'create_book.html'
    success_url = '/'

    model = Book
    fields = ['title', 'author', 'isbn', 'popularity']

from braces import views as braces_mixins

class BookDeleteView(braces_mixins.SuperuserRequiredMixin, DeleteView):
    model = Book
    success_url = '/'


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
