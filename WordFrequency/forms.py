from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Coupon


class UploadArticleForm(forms.Form):
    file = forms.FileField(label='檔案')


class RegistrationForm(UserCreationForm):
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
