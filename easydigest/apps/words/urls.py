from django.urls import path
from .views import save_word, user_words, article_words, explain_word

urlpatterns = [
    path('', save_word),
    path('explain/', explain_word),
    path('my/', user_words),
    path('article/<int:article_id>', article_words)
]