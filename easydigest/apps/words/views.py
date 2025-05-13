from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Word, LearnedWord
from .serializers import WordSerializer
from django.utils import timezone
from .gpt import explain_word_in_context
from apps.articles.models import Article

# 사용자가 단어 클릭하면 쉬운 설명 제공 + DB에 기록 저장
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learn_word(request):
    word_text = request.data.get('word_text')
    article_id = request.data.get('article_id')
    pos = request.data.get('pos')

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
    
    # 1. GPT로 쉬운 설명 생성
    description = explain_word_in_context(article.content, word_text)

    # 2. pos 분류 (추가 필요)
    pos = "명사"

    # 3. Word DB에 저장
    word_obj, created = Word.objects.get_or_create(
        user = request.user, word = word_text, 
        defaults = {"description": description, "pos": pos}
    )
    if not created:
        word_obj.ask_count += 1
        word_obj.last_learned = timezone.now()
        word_obj.description = description
        word_obj.save()
    
    # 4. LearnedWord DB에 저장
    _, created = LearnedWord.objects.get_or_create(
        user = request.user, word = word_obj, article = article
    )

    serializer = WordSerializer(word_obj)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    learned = LearnedWord.objects.filter(user = request.user, article = article_id)
    word_ids = learned.values_list('word_id', flat = True)
    words = Word.objects.filter(id__in = word_ids)
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)