from django.urls import path
from django.conf.urls import include

from . import views


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),

    path('authors/', views.authors, name='authors'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('create_book/', views.create_book, name='create_book'),
    path('delete_book', views.delete_book, name='delete_book'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('favorites/', views.favorites, name='favorites'),
    path('add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('remove-from-favorites/', views.remove_from_favorites, name='remove_from_favorites'),

    path('signup/', views.signup, name='signup'),

    path('', views.index, name='index'),
]
