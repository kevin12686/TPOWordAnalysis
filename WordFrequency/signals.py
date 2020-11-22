import re
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Article, Word, Frequency

# from .dictionaries import lookup_dictionaryapi

word_re = re.compile(r'[a-zA-Z]+')


@receiver(post_save, sender=Article)
def parse_word(sender, instance, *args, **kwargs):
    lower_content = instance.content.lower()
    words = word_re.findall(lower_content)
    for word in set(words):
        word_obj, _ = Word.objects.get_or_create(word=word)
        Frequency.objects.update_or_create(article=instance, word=word_obj, defaults={'count': words.count(word)})

# @receiver(post_save, sender=Word)
# def word_restore(sender, instance, created, *args, **kwargs):
#     if created:
#         result = lookup_dictionaryapi(instance.word)
#         if result:
#             instance.restored = result
#         else:
#             instance.restored = instance.word
#         instance.save()
