from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Article, LearnedArticle
from .serializers import ArticleSerializer, LearnedArticleSerializer
from .gpt import *
from .utils import crawl_news_content

# Create your views here.
@api_view(['POST', 'GET'])
def article_list(request):
    if request.method == 'POST':
        serializer = ArticleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        articles = Article.objects.all().order_by('-created_at')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_article(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': "URL is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    article, created = Article.objects.get_or_create(
        url=url,
        defaults={'content': crawl_news_content(url)}
    )

    # 여기에서 생성할지 따로 api 빼서 요청 들어오면 생성할지 고민 필요
    if created and not article.summary:
        article.summary = summarize_article(article.content)
        article.save()

    LearnedArticle.objects.get_or_create(user=request.user, article=article)

    serializer = ArticleSerializer(article)
    return Response(serializer.data)

@api_view(['GET'])
def article_detail(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ArticleSerializer(article)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_articles(request):
    learned_articles = LearnedArticle.objects.filter(user=request.user).select_related('article').order_by('-learned_at')
    serializer = LearnedArticleSerializer(learned_articles, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_summary(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

    if article.summary:
        return Response({'summary': article.summary}, status=status.HTTP_200_OK)

    # 1) Article summary
    raw_summary = summarize_article(article.content)

    # 1-2) Refining the summary with GPT
    summary = refine_summary_with_gpt(raw_summary)
    
    article.summary = summary
    article.save()

    return Response({'summary': summary}, status=status.HTTP_200_OK)