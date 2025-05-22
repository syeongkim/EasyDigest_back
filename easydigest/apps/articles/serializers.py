from rest_framework import serializers
from .models import Article, LearnedArticle
from .utils import crawl_news_content

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'url', 'content', 'summary', 'created_at']
        read_only_fields = ['id', 'url', 'content', 'summary', 'created_at']
    
class LearnedArticleSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = LearnedArticle
        fields = ['id', 'article', 'learned_at']