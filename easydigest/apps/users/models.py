from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(
        max_length=30,
        blank=False,
        null=False
    )
    email = models.EmailField(unique=True)

    class InterestChoices(models.TextChoices):
        POLITICS = "정치", "정치"
        SOCIAL = "사회", "사회"
        ECONOMY = "경제", "경제"
        CULTURE = "문화", "문화"
        TECHNOLOGY = "기술", "기술"
        ENTERTAIN = "연예", "연예"

    interest = models.CharField(
        max_length=20,
        choices=InterestChoices.choices,
        blank=True,
        null=True
    )

    @property
    def total_correct_count(self):
        from apps.words.models import Word
        result = Word.objects.filter(user=self).aggregate(total=models.Sum('correct_count'))
        return result['total'] or 0
    
    @property
    def level(self):
        correct = self.total_correct_count
        if correct < 20:
            return 1 
        elif correct < 40:
            return 2
        elif correct < 60:
            return 3
        elif correct < 80:
            return 4
        else:
            return 5

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)