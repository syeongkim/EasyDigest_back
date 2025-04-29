from django.urls import path
from .views import article_list, article_detail

urlpatterns = [
    path('', article_list),
    path('<int:article_id>/', article_detail)
]