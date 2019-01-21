from django.urls import path
from django.conf.urls import include
from django.views.generic import RedirectView
from . import views


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),

    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),

    path('book/', views.CreateBookView.as_view(), name='book_create'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:pk>/update', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/delete', views.BookDeleteView.as_view(), name='book_delete'),

    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('favorites/', views.favorites, name='favorites'),
    path('add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('remove-from-favorites/', views.remove_from_favorites, name='remove_from_favorites'),

    path('signup/', views.signup, name='signup'),
    path('', views.IndexView.as_view(), name='index'),
]
