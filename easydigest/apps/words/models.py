from django.db import models
from django.conf import settings
from apps.articles.models import Article

# Create your models here.
# 유저 - 단어별 총 학습 정보
class Word(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    description = models.TextField()
    pos = models.CharField(max_length=30)
    synonym = models.CharField(max_length=200, blank=True, null=True)
    antonym = models.CharField(max_length=200, blank=True, null=True)
    example = models.TextField(blank=True, null=True)
    ask_count = models.IntegerField(default=1)
    correct_count = models.IntegerField(default=0)
    last_learned = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'word')
    
    def __str__(self):
        return f"{self.word} ({self.user.username})"

# 어떤 유저가 어떤 기사에서 어떤 단어를 학습했는지 저장
class LearnedWord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    learned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'word', 'article')

    def __str__(self):
        return f"{self.word.word} - {self.article.content[:10] ({self.user.username})}"