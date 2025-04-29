from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'content', 'summary', 'created_at']
        read_only_fields = ['user', 'summary', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        return Article.objects.create(user=user, **validated_data)