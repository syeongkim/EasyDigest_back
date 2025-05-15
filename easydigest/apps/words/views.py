from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Word, LearnedWord
from .serializers import WordSerializer
from django.utils import timezone
from .gpt import analyze_pos_with_stanza, infer_overall_pos, retrieve_definition, generate_definition_with_gpt
from apps.articles.models import Article
import re, random

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
    # description = explain_word_in_context(article.content, word_text)
    description = retrieve_definition(word_text)
    if not description:
        description = generate_definition_with_gpt(word_text)

    # 2. pos 분류 (추가 필요)
    toks = analyze_pos_with_stanza(word_text)
    pos = infer_overall_pos(toks)

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

# 퀴즈 생성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quiz(request):
    article_id = request.data.get("article_id")
    
    if not article_id:
        return Response(
            {"message": "article id is required"},
             status = status.HTTP_400_BAD_REQUEST
        )
    
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response(
            {"message": "Article not found"},
            status = status.HTTP_404_NOT_FOUND
        )
    
    # 기사 본문에서 등장하는 단어 추출
    article_text = article.content
    words_in_article = list(set(re.findall(r'\b[가-힣]{2,}\b', article_text)))
    print("article_text", article_text)
    print("words_in_article", words_in_article)

    # 기사에 등장한 단어들 중에서 과거에 학습한 단어만 추출
    past_learned_words = Word.objects.filter(
        user=request.user,
        word__in=words_in_article
    )

    if not past_learned_words.exists():
        return Response(
            {"message": "사용자가 과거에 학습한 단어가 없습니다."},
             status=status.HTTP_200_OK
        )
    
    # 이번에 학습한 단어들 조회
    learned_in_this_article = LearnedWord.objects.filter(
        user=request.user,
        article=article
    ).values_list("word__word", flat=True)

    # 퀴즈 후보 선정 (기사에 등장한 단어들 중에서 이번에 학습하진 않았지만, 과거에는 학습했던 단어들)
    quiz_candidates = past_learned_words.exclude(
        word__in = learned_in_this_article
    ).filter(correct_count__lt=3)

    if not quiz_candidates.exists():
        return Response(
            {"message": "퀴즈로 낼 단어가 없습니다."},
            status=status.HTTP_200_OK
        )
    
    # 퀴즈 단어 선택
    quiz_word = random.choice(list(quiz_candidates))
    pos = quiz_word.pos

    # 보기 구성
    distractors = Word.objects.filter(
        user = request.user,
        pos = pos,
        correct_count__lt=3
    ).exclude(id=quiz_word.id)

    distractors = list(distractors)
    random.shuffle(distractors)
    distractors = distractors[:3]

    choices = distractors + [quiz_word]
    random.shuffle(choices)

    serializer = WordSerializer(choices, many=True)

    # question_word: 문제를 낼 단어 -> 설명을 문제로 내면 될 듯
    # choices: question_word를 포함한 보기 4개
    return Response({
        "question_word": quiz_word.word,
        "choices": serializer.data
    })

# 퀴즈 결과 기록
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request):
    question_word_id = request.data.get("question_word_id") # 정답인 단어의 id (correct_count를 증가시킬 단어의 id)
    is_correct = request.data.get("is_correct") # 퀴즈 정답 여부

    if question_word_id is None:
        return Response(
            {"message": "question_word_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if is_correct is None:
        return Response(
            {"message": "is_correct is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        word = Word.objects.get(id=question_word_id, user=request.user)
    except Word.DoesNotExist:
        return Response(
            {"message": "단어를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if is_correct:
        word.correct_count += 1
        word.save()

    serializer = WordSerializer(word)

    return Response(
        {
            "message": "정답 기록 완료",
            "is_correct": is_correct,
            "word": serializer.data
        },
        status = status.HTTP_200_OK
    )
    