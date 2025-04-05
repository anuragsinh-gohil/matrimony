from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'required': True}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'required': True}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class GeneralInfoForm(forms.ModelForm):
    visa_other = forms.CharField(
        max_length=50, 
        required=False, 
        label="Specify Other Visa Status", 
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    confirmation_code = forms.CharField(
        label="Enter code which you will get from above selected referred by person",
        widget=forms.TextInput(attrs={'class': 'form-input', 'required': True})
    )
    
    class Meta:
        model = Profile
        fields = [
            'name', 'current_address', 'gender', 'birth_date', 'phone_number', 
            'confirmation_code', 'referred_by', 'marital_status', 'canada_us_citizen', 
            'visa_status', 'height', 'weight', 'birth_time', 'education', 
            'occupation', 'about_yourself', 'food_preference', 'city', 'state', 'siblings'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'required': True}),
            'birth_time': forms.TextInput(attrs={'class': 'form-input', 'required': True}),  # Changed to TextInput
            'about_yourself': forms.Textarea(attrs={'class': 'form-textarea', 'required': True}),
            'siblings': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'current_address': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'gender': forms.Select(attrs={'class': 'form-dropdown', 'required': True}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'marital_status': forms.Select(attrs={'class': 'form-dropdown', 'required': True}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'required': True, 'step': '0.1', 'min': '0'}),  # Numeric input
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'required': True, 'step': '0.1', 'min': '0'}),  # Numeric input
            'education': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'occupation': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'food_preference': forms.Select(attrs={'class': 'form-dropdown', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'referred_by': forms.Select(attrs={'class': 'form-dropdown', 'required': True, 'id': 'id_referred_by'}),
            'visa_status': forms.Select(attrs={'class': 'form-dropdown'}),
            'canada_us_citizen': forms.Select(attrs={'class': 'form-dropdown', 'required': True}),  # Changed to dropdown
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['referred_by'].queryset = User.objects.filter(is_staff=True)

class FamilyPhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'father_name', 'father_native', 'father_number', 'father_location', 
            'father_occupation', 'father_siblings', 'father_maternal', 
            'grandfather_name', 'grandmother_name', 'mother_name', 
            'mother_father_name', 'mother_maternal', 'full_body_image', 
            'half_body_image', 'extra_image1', 'extra_image2', 'extra_image3'
        ]
        widgets = {
            'father_siblings': forms.Textarea(attrs={'class': 'form-textarea', 'required': True}),
            'father_maternal': forms.Textarea(attrs={'class': 'form-textarea', 'required': True}),
            'mother_maternal': forms.Textarea(attrs={'class': 'form-textarea', 'required': True}),
            'father_name': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'father_native': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'father_number': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'father_location': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'father_occupation': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'grandfather_name': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'grandmother_name': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'mother_name': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'mother_father_name': forms.TextInput(attrs={'class': 'form-input', 'required': True}),
            'full_body_image': forms.FileInput(attrs={'class': 'form-file', 'required': True}),
            'half_body_image': forms.FileInput(attrs={'class': 'form-file', 'required': True}),
            'extra_image1': forms.FileInput(attrs={'class': 'form-file'}),
            'extra_image2': forms.FileInput(attrs={'class': 'form-file'}),
            'extra_image3': forms.FileInput(attrs={'class': 'form-file'}),
        }