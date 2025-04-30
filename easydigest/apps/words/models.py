from django.db import models
from django.conf import settings
from apps.articles.models import Article

# Create your models here.
class Word(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    description = models.TextField()
    pos = models.CharField(max_length=30)
    synonym = models.CharField(max_length=200, blank=True, null=True)
    antonym = models.CharField(max_length=200, blank=True, null=True)
    example = models.TextField(blank=True, null=True)
    ask_count = models.IntegerField(default=1)
    correct_count = models.IntegerField(default=0)
    last_learned = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.word} ({self.user.username})"