import re
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.db.models import Sum
from django.urls import reverse
from django.views.generic import FormView, ListView
from django.views.generic.base import View, TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .dictionaries import lookup_dictionaryapi_parse, lookup_dictionaryapi
from .forms import UploadArticleForm, RegistrationForm, NoteForm
from .models import Article, Word, Frequency, Stopwords, Learned, Note


# Create your views here.

class SuperuserPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class RegistrationView(FormView):
    form_class = RegistrationForm
    template_name = 'registerForm.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('rank')


class Tools(SuperuserPermissionMixin, TemplateView):
    template_name = 'tools.html'

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['article_count'] = Article.objects.all().count()
        content['word_count'] = Word.objects.all().count()
        content['restored_count'] = Word.objects.exclude(restored='').count()
        return content


class UploadArticle(SuperuserPermissionMixin, FormView):
    form_class = UploadArticleForm
    template_name = 'uploadForm.html'

    def form_valid(self, form):
        articles = form.cleaned_data['file'].read().decode()
        articles = articles.replace('\r', '')
        articles = re.sub(r'\n\s*\n', '\n', articles)
        first = True
        next_is_title = False
        for line in articles.split('\n'):
            if re.match(r'^\d+_\d+$', line):
                if first:
                    first = False
                else:
                    Article.objects.update_or_create(title=title, defaults={'content': '\n'.join(content)})
                next_is_title = True
                title = ''
                content = list()
            elif not first:
                if next_is_title:
                    title = line
                    next_is_title = False
                else:
                    content.append(line)
        return self.get_success_url()

    def get_success_url(self):
        return render(self.request, 'notify.html', {'title': '上傳狀態', 'content': '成功'})


class WordRestore(SuperuserPermissionMixin, View):
    def get(self, request, *args, **kwargs):
        parse = request.GET.get('parse')
        if parse == '1':
            for w in Word.objects.filter(restored=''):
                try:
                    rw, js = lookup_dictionaryapi_parse(w.word)
                    if rw:
                        w.restored = rw
                        w.raw_json = js
                        w.save()
                except Exception:
                    pass
            return render(self.request, 'notify.html', {'title': '線上還原狀態', 'content': '成功'})
        else:
            for w in Word.objects.exclude(raw_json=''):
                try:
                    rw, js = lookup_dictionaryapi(w.word, w.raw_json)
                    if w.restored != rw:
                        w.restored = rw
                        w.save()
                except Exception:
                    pass
            return render(self.request, 'notify.html', {'title': '本地還原狀態', 'content': '成功'})


class Ranking(LoginRequiredMixin, ListView):
    model = Frequency
    template_name = 'ranking.html'
    paginate_by = 50

    def get_queryset(self):
        return Frequency.objects.exclude(word__restored__in=Stopwords.objects.all().values('word')).exclude(word__restored__in=Learned.objects.filter(user=self.request.user).values('word')).exclude(word__restored='').order_by('word__restored').values('word__restored').distinct().annotate(
            times=Sum('count')).filter(times__gt=0).order_by('-times')


class RankingXSLX(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="word_frequency.xlsx"'
        wb = Workbook()
        ws = wb.active
        ws.title = 'frequency'
        ws.append(['Word', 'Count'])
        for data in Frequency.objects.exclude(word__restored__in=Stopwords.objects.all().values('word')).exclude(word__restored='').order_by('word__restored').values('word__restored').distinct().annotate(times=Sum('count')).filter(times__gt=0).order_by('-times'):
            ws.append([data['word__restored'], data['times']])
        response.write(save_virtual_workbook(wb))
        return response


class StopwordsList(SuperuserPermissionMixin, ListView):
    model = Stopwords
    template_name = 'stopword.html'


class StopwordsCreate(SuperuserPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        word = request.POST.get('word')
        try:
            Stopwords.objects.get_or_create(word=word)
        except ValidationError:
            pass
        return HttpResponseRedirect(reverse('rank'))


class StopwordsDelete(SuperuserPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        word = request.POST.get('word')
        try:
            Stopwords.objects.get(word=word).delete()
        except Stopwords.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('stopwords'))


class LearnedList(LoginRequiredMixin, ListView):
    model = Learned
    template_name = 'learned.html'
    paginate_by = 50

    def get_queryset(self):
        return Learned.objects.filter(user=self.request.user)


class LearnedCreate(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        word = request.POST.get('word')
        try:
            Learned.objects.get_or_create(user=request.user, word=word)
        except ValidationError:
            pass
        return HttpResponseRedirect(reverse('rank'))


class LearnedDelete(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        word = request.POST.get('word')
        try:
            Learned.objects.get(user=request.user, word=word).delete()
        except Learned.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('learnedList'))


class NoteDetail(LoginRequiredMixin, TemplateView):
    template_name = 'note.html'

    def get(self, request, *args, **kwargs):
        self.word = self.kwargs.get('word')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            note = Note.objects.get(user=self.request.user, word=self.word)
            context['word'] = self.word
            context['note'] = note.note
            context['exist'] = True
        except Note.DoesNotExist:
            context['exist'] = False
        return context


class NoteList(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'noteList.html'
    paginate_by = 50

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)


class NoteEdit(LoginRequiredMixin, FormView):
    template_name = 'editNote.html'
    form_class = NoteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user, 'word': self.kwargs.get('word')})
        try:
            obj = Note.objects.get(user=self.request.user, word=self.kwargs.get('word'))
            kwargs.update({'instance': obj})
        except Note.DoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('noteDetail', kwargs={'word': self.kwargs.get('word')})


class NoteDelete(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        word = request.POST.get('word')
        try:
            Note.objects.get(user=request.user, word=word).delete()
        except Note.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('noteList'))


class ArticleDetail(LoginRequiredMixin, TemplateView):
    template_name = 'article.html'

    def get(self, request, *args, **kwargs):
        self.article = self.kwargs.get('article')
        self.highlight = request.GET.get('highlight')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            article = Article.objects.get(title=self.article)
            context['title'] = article.title
            context['content'] = article.content
            context['exist'] = True

            context['highlight'] = ''
            if self.highlight:
                related = Word.objects.filter(restored=self.highlight).values_list('word', flat=True)
                if related.exists():
                    context['highlight'] = '(%s)' % '|'.join(related)

        except Article.DoesNotExist:
            context['exist'] = False
        return context


class WordDetail(LoginRequiredMixin, TemplateView):
    template_name = 'word.html'

    def get(self, request, *args, **kwargs):
        self.word = self.kwargs.get('word')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        word = Word.objects.filter(restored=self.word)
        context['exist'] = word.exists()
        if not context['exist']:
            try:
                self.word = Word.objects.get(word=self.word).restored
                word = Word.objects.filter(restored=self.word)
                context['exist'] = word.exists()
            except Word.DoesNotExist:
                pass
        if context['exist']:
            feq = Frequency.objects.filter(word__restored=self.word)
            context['word'] = self.word
            context['times'] = feq.aggregate(Sum('count'))['count__sum']
            context['related'] = word
            context['articles'] = feq.values('article').order_by('article').distinct().annotate(sum=Sum('count')).order_by('-sum')
            context['learned'] = Learned.objects.filter(user=self.request.user, word=self.word)
            context['stopword'] = Stopwords.objects.filter(word=self.word)
        return context
