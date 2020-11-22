from django import forms


class UploadArticleForm(forms.Form):
    file = forms.FileField(label='檔案')
