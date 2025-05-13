from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Word
from .serializers import WordSerializer
from django.utils import timezone
from .kogpt import explain_word_in_context
from apps.articles.models import Article

# 사용자가 학습한 단어를 words DB에 저장
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

# 사용자가 단어를 클릭하면 KoGPT로 생성한 쉬운 설명 제공
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def explain_word(request):
    word_text = request.data.get('word')
    article_id = request.data.get('article')

    if not word_text:
        return Response(
            {"message": "word is required"},
            status = status.HTTP_400_BAD_REQUEST
        )

    if not article_id:
        return Response(
            {"message": "article id is requires"},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response(
            {"message": "article does not exist"},
            status = status.HTTP_404_NOT_FOUND
        )
    
    explanation = explain_word_in_context(article.content, word_text)

    return Response({
        "word": word_text,
        "explanation": explanation
    })

# 사용자가 학습한 모든 단어 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_words(request):
    words = Word.objects.filter(user=request.user).order_by('-last_learned')
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)

# 사용자가 학습한 단어를 기사별로 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def article_words(request, article_id):
    words = Word.objects.filter(user=request.user, article=article_id).order_by('-last_learned')
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)