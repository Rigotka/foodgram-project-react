from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    firs_name = models.CharField(max_length=154)
    last_name = models.CharField(max_length=154)
    username = models.CharField(unique=True, max_length=154)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,related_name='subscriber')
    author = models.ForeignKey(User,on_delete=models.CASCADE)

    

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='subscription'),
        ]

    def __str__(self):
        return f'{self.user} na {self.author}'