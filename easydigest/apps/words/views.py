from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Word
from .serializers import WordSerializer
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_word(request):
    data = request.data
    word_text = data.get('word')
    article_id = data.get('article')

    word_instance = Word.objects.filter(
        user=request.user, word=word_text, article_id=article_id
    ).first()

    if word_instance:
        word_instance.ask_count += 1
        word_instance.last_learned = timezone.now()
        word_instance.save()
        serializer = WordSerializer(word_instance)
        return Response(serializer.data)
    
    serializer = WordSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_words(request):
    words = Word.objects.filter(user=request.user).order_by('-last_learned')
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def article_words(request, article_id):
    words = Word.objects.filter(user=request.user, article=article_id).order_by('-last_learned')
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)