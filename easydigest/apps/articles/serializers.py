from rest_framework import serializers
from .models import Article
from .utils import crawl_news_content

class ArticleSerializer(serializers.ModelSerializer):
    url = serializers.URLField(write_only=True)

    class Meta:
        model = Article
        fields = ['id', 'user', 'url', 'content', 'summary', 'created_at']
        read_only_fields = ['user', 'content', 'summary', 'created_at', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        url = validated_data.pop('url')

        content = crawl_news_content(url)

        return Article.objects.create(user=user, content=content, **validated_data)