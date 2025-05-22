from django.urls import path
from .views import *

urlpatterns = [
    path('', register_article),
    path('<int:article_id>/', article_detail),
    path('my/', my_articles),
    path('<int:article_id>/generate-summary/', generate_summary)
]