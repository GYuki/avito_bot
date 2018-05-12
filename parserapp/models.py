from django.db import models

# Create your models here.


class Chat(models.Model):
    telegram_chat_id = models.IntegerField(unique=True)


class Category(models.Model):
    name = models.CharField(max_length=30)
    cmd = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class CategorySubscriber(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Advert(models.Model):
    avito_id = models.IntegerField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
