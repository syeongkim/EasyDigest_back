from rest_framework import serializers
from .models import Word

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'
        read_only_fields = ['ask_count', 'correct_count', 'last_learned', 'user']