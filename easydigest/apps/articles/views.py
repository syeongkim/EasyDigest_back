from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Article
from .serializers import ArticleSerializer
from .gpt import summarize_article

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
    user = request.user
    articles = Article.objects.filter(user=user).order_by('-created_at')
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_summary(request, article_id):
    try:
        article = Article.objects.get(id=article_id, user=request.user)
    except Article.DoesNotExist:
        return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

    if article.summary:
        return Response({'summary': article.summary}, status=status.HTTP_200_OK)

    summary = summarize_article(article.content)
    article.summary = summary
    article.save()

    return Response({'summary': summary}, status=status.HTTP_200_OK)