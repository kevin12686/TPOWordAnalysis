from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=255, primary_key=True, verbose_name='Title')
    content = models.TextField(verbose_name='Content')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['title', ]
        verbose_name = 'Article'


class Word(models.Model):
    word = models.CharField(max_length=255, primary_key=True, verbose_name='Word')
    restored = models.CharField(max_length=255, blank=True, verbose_name='Restored')
    raw_json = models.TextField(blank=True, verbose_name='RAW JSON')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['word']
        verbose_name = 'Word'


class Frequency(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ['article', 'word']
        ordering = ['article', 'word', 'count']
        verbose_name = 'Frequency'


class Stopwords(models.Model):
    word = models.CharField(max_length=255, primary_key=True, verbose_name='Word')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['word']
        verbose_name = 'Stopwords'


class Learned(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='learned', verbose_name='User')
    word = models.CharField(max_length=255, verbose_name='Word')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ['user', 'word']
        ordering = ['user', 'word']
        verbose_name = 'Learned'


class Coupon(models.Model):
    code = models.CharField(max_length=255, primary_key=True, verbose_name='code')
    available = models.BooleanField(default=True, verbose_name='available')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['code']
        verbose_name = 'Coupon'
