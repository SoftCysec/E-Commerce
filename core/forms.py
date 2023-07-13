from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = {
    ('S','Stripe'),
    ('P', 'Paypal'),
    ('B', 'Bank Transfer')
}

class CheckoutForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Jones', 'class':'form-control'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Alukwe', 'class':'form-control'}), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'example@email.com', 'class':'form-control'}), required=False)
    mobile_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'+123 456 789', 'class':'form-control'}), required=False)
    shipping_street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'123 Main Street', 'class':'form-control'}), required=False)
    shipping_apartment_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Apartmen or suite', 'class':'form-control'}), required=False)
    shipping_country = CountryField(blank_label='(Select Country)').formfield(widget=CountrySelectWidget(attrs={'class':'custom-select'}), required=False)
    shipping_city = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'New York', 'class':'form-control'}), required=False)
    shipping_state = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'New York', 'class':'form-control'}), required=False)
    shipping_zip_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'123', 'class':'form-control'}), required=False)
    # /billing 
    billing_street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'123 Main Street', 'class':'form-control'}), required=False)
    billing_apartment_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Apartmen or suite', 'class':'form-control'}), required=False)
    billing_country = CountryField(blank_label='(Select Country)').formfield(widget=CountrySelectWidget(attrs={'class':'custom-select'}), required=False)
    billing_city = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'New York', 'class':'form-control'}), required=False)
    billing_state = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'New York', 'class':'form-control'}), required=False)
    billing_zip_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'123', 'class':'form-control'}), required=False)
   
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    set_default_shipping =forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    use_default_shipping =forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    
    set_default_billing =forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    use_default_billing =forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    create_account = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    ship_to_different_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(required=True, widget=forms.RadioSelect(), choices=PAYMENT_CHOICES )

class CouponForm(forms.Form):
        code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Coupon Code', 'class':'form-control border-0 p-4'}))

class RefundForm(forms.Form):
        ref_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Refund Code',
                                                                 'class':'form-control',
                                                                 'data-validation-required-message':'Please enter your refund code', 
                                                                 'id':"name"}))
        email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Your Email',
                                                                'class':'form-control',
                                                                 'data-validation-required-message':'Please enter your email', 
                                                                 'id':"email"}))
        message = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Message',
                                                                 'class':'form-control',
                                                                 'data-validation-required-message':'Please enter your message', 
                                                                 'id':"message", 'rows':'8'}))

class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
