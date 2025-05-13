from django.urls import path
from .views import learn_word, user_words, article_words, generate_quiz

urlpatterns = [
    path('learn/', learn_word),
    path('my/', user_words),
    path('article/<int:article_id>', article_words),
    path('generate-quiz/', generate_quiz)
]