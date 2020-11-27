from django.contrib import admin
from .models import Article, Word, Frequency, Stopwords, Learned, Note, Coupon


# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title']


class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'restored']


class FrequencyAdmin(admin.ModelAdmin):
    list_display = ['word', 'article', 'count']


class StopwordsAdmin(admin.ModelAdmin):
    list_display = ['word']


class LearnedAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'timestamp']


class NoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'timestamp']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'available']


admin.site.register(Article, ArticleAdmin)
admin.site.register(Word, WordAdmin)
admin.site.register(Frequency, FrequencyAdmin)
admin.site.register(Stopwords, StopwordsAdmin)
admin.site.register(Learned, LearnedAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Coupon, CouponAdmin)
