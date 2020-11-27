from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Coupon, Note


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            field = self.fields[name]
            attrs = field.widget.attrs
            if not attrs.get('class'):
                attrs.update({'class': 'form-control'})

    def is_valid(self):
        result = super().is_valid()
        for x in self.errors:
            if x != '__all__':
                attrs = self.fields[x].widget.attrs
                attrs.update({'class': attrs.get('class', '') + ' is-invalid'})
        return result


class UploadArticleForm(forms.Form):
    file = forms.FileField(label='檔案')


class RegistrationForm(UserCreationForm, BootstrapModelForm):
    coupon = forms.CharField(label='Coupon')

    def clean_coupon(self):
        coupon = self.cleaned_data['coupon']
        try:
            self.coupon_obj = Coupon.objects.get(code=coupon, available=True)
        except Coupon.DoesNotExist:
            self.add_error('coupon', 'Invalid coupon.')
        return coupon

    def save(self, commit=True):
        self.coupon_obj.available = False
        self.coupon_obj.save()
        return super().save(commit=commit)


class NoteForm(BootstrapModelForm):
    word = forms.CharField(widget=forms.TextInput(attrs={'readonly': True}), label='Word')

    def __init__(self, user, word, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.word = word
        self.fields['word'].initial = self.word

    def save(self, commit=True):
        self.instance.user = self.user
        self.instance.word = self.word
        return super().save(commit=commit)

    field_order = ['word', 'note']

    class Meta:
        model = Note
        fields = ['note']
