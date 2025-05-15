from django.urls import path
from .views import article_list, article_detail, my_articles, generate_summary

urlpatterns = [
    path('', article_list),
    path('<int:article_id>/', article_detail),
    path('my/', my_articles),
    path('<int:article_id>/generate-summary/', generate_summary)
]