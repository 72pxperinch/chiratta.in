from django import forms


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(label='Email')
    country = forms.CharField()
    street_address = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    pin_code = forms.IntegerField()
    phone_number = forms.IntegerField()


class SendMessageForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(label='Email')
    message = forms.CharField(max_length=2048)