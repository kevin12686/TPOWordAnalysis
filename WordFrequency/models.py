from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=255, primary_key=True, verbose_name='Title')
    content = models.TextField(verbose_name='Content')

    class Meta:
        ordering = ['title', ]
        verbose_name = 'Article'


class Word(models.Model):
    word = models.CharField(max_length=255, primary_key=True, verbose_name='Word')
    restored = models.CharField(max_length=255, blank=True, verbose_name='Restored')
    raw_json = models.TextField(blank=True, verbose_name='RAW JSON')

    class Meta:
        ordering = ['word']
        verbose_name = 'Word'


class Frequency(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['article', 'word', 'count']
        verbose_name = 'Frequency'


class Stopwords(models.Model):
    word = models.CharField(max_length=255, primary_key=True, verbose_name='Word')

    class Meta:
        ordering = ['word']
        verbose_name = 'Stopwords'


class Learned(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='learned', verbose_name='User')
    word = models.CharField(max_length=255, verbose_name='Word')

    class Meta:
        ordering = ['user', 'word']
        verbose_name = 'Learned'
