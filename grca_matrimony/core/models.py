from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    MARITAL_CHOICES = [('N', 'Never Been Married'), ('D', 'Divorced')]
    FOOD_CHOICES = [('V', 'Veg'), ('N', 'Non-Veg')]
    VISA_CHOICES = [('F1', 'F1'), ('H1B', 'H1B'), ('Other', 'Other')]
    CITIZEN_CHOICES = [('Y', 'Yes'), ('N', 'No')]
    
    # Default image paths
    DEFAULT_FULL_BODY_IMAGE = 'profiles/default_full_body.jpg'
    DEFAULT_HALF_BODY_IMAGE = 'profiles/default_half_body.jpg'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True)
    name = models.CharField(max_length=100, default="Enter Name")
    current_address = models.CharField(max_length=200, default="Enter Address")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birth_date = models.DateField(default='2000-01-01')  # Dummy date
    age = models.IntegerField(default=0)
    confirmation_code = models.CharField(max_length=6, default="000000")
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='referred_profiles', limit_choices_to={'is_superuser': True}, null=True, default=None)
    marital_status = models.CharField(max_length=1, choices=MARITAL_CHOICES, default='N')
    phone_number = models.CharField(max_length=15, default="000-000-0000")
    canada_us_citizen = models.CharField(max_length=1, choices=CITIZEN_CHOICES, default='N')
    visa_status = models.CharField(max_length=10, choices=VISA_CHOICES, default='Other')
    height = models.FloatField(default=0.0)
    weight = models.FloatField(default=0.0)
    birth_time = models.CharField(max_length=10, default='12:00')
    education = models.CharField(max_length=100, default="Enter Education")
    occupation = models.CharField(max_length=100, default="Enter Occupation")
    about_yourself = models.TextField(default="No information provided")
    food_preference = models.CharField(max_length=1, choices=FOOD_CHOICES, default='V')
    city = models.CharField(max_length=100, default="Enter City")
    state = models.CharField(max_length=100, default="Enter State")
    siblings = models.TextField(default="None")
    native = models.CharField(max_length=100, default='Enter Native')

    # Family Information (Part 3)
    father_name = models.CharField(max_length=100, default="Enter Father Name")
    father_native = models.CharField(max_length=100, default="Enter Father Native")
    father_number = models.CharField(max_length=15, default="000-000-0000")
    father_location = models.CharField(max_length=100, default="Enter Location")
    father_occupation = models.CharField(max_length=100, default="Enter Occupation")
    father_siblings = models.TextField(default="None")
    father_maternal = models.TextField(default="None")
    grandfather_name = models.CharField(max_length=100, default="Enter Grandfather Name")
    grandmother_name = models.CharField(max_length=100, default="Enter Grandmother Name")
    mother_name = models.CharField(max_length=100, default="Enter Mother Name")
    mother_father_name = models.CharField(max_length=100, default="Enter Mother's Father Name")
    mother_maternal = models.TextField(default="None")
    
    # Image Fields with Defaults
    full_body_image = models.ImageField(upload_to='profiles/', default=DEFAULT_FULL_BODY_IMAGE)
    half_body_image = models.ImageField(upload_to='profiles/', default=DEFAULT_HALF_BODY_IMAGE)
    extra_image1 = models.ImageField(upload_to='profiles/', null=True, blank=True, default='profiles/default_image.jpg')
    extra_image2 = models.ImageField(upload_to='profiles/', null=True, blank=True, default='profiles/default_image.jpg')
    extra_image3 = models.ImageField(upload_to='profiles/', null=True, blank=True, default='profiles/default_image.jpg')

    def save(self, *args, **kwargs):
        # Automatically update age based on birth_date
        self.age = (timezone.now().date() - self.birth_date).days // 365
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200, default="Dummy Event Title")
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(default="No description provided")

    def __str__(self):
        return self.title

class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=None, null=True)
    reminder_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
