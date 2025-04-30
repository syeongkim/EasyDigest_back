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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)