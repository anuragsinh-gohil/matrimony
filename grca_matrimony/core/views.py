from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from .models import Profile, Event, Reminder
from .forms import UserForm, GeneralInfoForm, FamilyPhotoForm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt  # Temporarily for debugging AJAX
def send_referral_code(request):
    if request.method == 'POST':
        referred_by_id = request.POST.get('referred_by_id')
        if not referred_by_id:
            return JsonResponse({'status': 'error', 'message': 'No referrer ID provided.'})
        
        try:
            referred_by = User.objects.get(id=referred_by_id, is_staff=True)
            confirmation_code = str(random.randint(100000, 999999))
            request.session['confirmation_code'] = confirmation_code
            send_mail(
                'GRCA Referral Code',
                f'A new user has selected you as their referrer. The code is: {confirmation_code}',
                'anuragsinh.gohil98@gmail.com',
                [referred_by.email],
                fail_silently=False,
            )
            print(f"Email sent to {referred_by.email} with code: {confirmation_code}")
            return JsonResponse({'status': 'success', 'message': 'Code has been sent.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid referrer.'})
        except Exception as e:
            print(f"Error in send_referral_code: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Server error: {str(e)}"})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def events(request):
    events = Event.objects.all()
    return render(request, 'core/events.html', {'events': events})

def contact(request):
    return render(request, 'core/contact.html')

def blog(request):
    return render(request, 'core/blog.html')

def register(request):
    if request.method == 'POST':
        step = request.POST.get('step')
        
        if step == '1':
            if not request.POST.get('agree'):
                messages.error(request, "You must agree to the terms.")
                return render(request, 'core/register_step1.html')
            request.session['step1_complete'] = True
            return render(request, 'core/register_step2.html', {
                'user_form': UserForm(),
                'general_form': GeneralInfoForm()
            })
        
        elif step == '2':
            user_form = UserForm(request.POST)
            general_form = GeneralInfoForm(request.POST)
            if user_form.is_valid() and general_form.is_valid():
                request.session['user_data'] = user_form.cleaned_data
                general_data = general_form.cleaned_data
                
                print(f"birth_date type before serialization: {type(general_data['birth_date'])}")
                print(f"birth_date value: {general_data['birth_date']}")
                
                general_data_serializable = general_data.copy()
                if 'birth_date' in general_data_serializable and isinstance(general_data_serializable['birth_date'], date):
                    general_data_serializable['birth_date'] = general_data_serializable['birth_date'].isoformat()
                if 'referred_by' in general_data_serializable and general_data_serializable['referred_by']:
                    general_data_serializable['referred_by'] = general_data_serializable['referred_by'].id
                
                print(f"Serialized general_data: {general_data_serializable}")
                request.session['general_data'] = general_data_serializable
                
                entered_code = general_data['confirmation_code']
                if entered_code != request.session.get('confirmation_code'):
                    messages.error(request, "Invalid code. Please enter the correct code sent to the referrer.")
                    return render(request, 'core/register_step2.html', {
                        'user_form': user_form,
                        'general_form': general_form
                    })
                
                messages.success(request, "Code matched successfully!")
                return render(request, 'core/register_step3.html', {
                    'family_form': FamilyPhotoForm()
                })
            return render(request, 'core/register_step2.html', {
                'user_form': user_form,
                'general_form': general_form
            })
        
        elif step == '3':
            family_form = FamilyPhotoForm(request.POST, request.FILES)
            if family_form.is_valid():
                user_data = request.session.get('user_data')
                general_data = request.session.get('general_data')
                if not user_data or not general_data:
                    return redirect('register')
                
                general_data_working = general_data.copy()
                if 'birth_date' in general_data_working and general_data_working['birth_date']:
                    general_data_working['birth_date'] = date.fromisoformat(general_data_working['birth_date'])
                referred_by_id = general_data_working.get('referred_by')
                general_data_working['referred_by'] = User.objects.get(id=referred_by_id) if referred_by_id else None
                
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )
                
                visa_status = general_data_working['visa_status']
                if visa_status == 'Other':
                    visa_status = request.POST.get('visa_other', '')
                
                profile = Profile(
                    user=user,
                    name=general_data_working['name'],
                    current_address=general_data_working['current_address'],
                    gender=general_data_working['gender'],
                    birth_date=general_data_working['birth_date'],
                    age=(timezone.now().date() - general_data_working['birth_date']).days // 365,
                    phone_number=general_data_working['phone_number'],
                    confirmation_code=request.session.get('confirmation_code'),
                    referred_by=general_data_working['referred_by'],
                    marital_status=general_data_working['marital_status'],
                    canada_us_citizen=general_data_working['canada_us_citizen'],
                    visa_status=visa_status if general_data_working['canada_us_citizen'] == 'N' else '',
                    height=general_data_working['height'],
                    weight=general_data_working['weight'],
                    birth_time=general_data_working['birth_time'],
                    education=general_data_working['education'],
                    occupation=general_data_working['occupation'],
                    about_yourself=general_data_working['about_yourself'],
                    food_preference=general_data_working['food_preference'],
                    city=general_data_working['city'],
                    state=general_data_working['state'],
                    siblings=general_data_working['siblings'],
                    **family_form.cleaned_data
                )
                profile.save()
                print(f"Profile created for user: {user.username}")
                
                request.session['general_data'] = general_data
                login(request, user)
                for key in ['step1_complete', 'user_data', 'general_data', 'confirmation_code']:
                    request.session.pop(key, None)
                return redirect('profile_list')
            return render(request, 'core/register_step3.html', {'family_form': family_form})
    
    return render(request, 'core/register_step1.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not hasattr(user, 'profile'):
                birth_date = date(2000, 1, 1)
                age = (timezone.now().date() - birth_date).days // 365
                print(f"Creating default profile for {user.username} on login")
                Profile.objects.create(
                    user=user,
                    name=user.username,
                    birth_date=birth_date,
                    age=age,
                    weight=0.0  # Default weight to satisfy NOT NULL
                )
            return redirect('profile_list')
        messages.error(request, 'Invalid credentials')
    return render(request, 'core/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def my_account(request):
    print(f"User: {request.user.username}, Authenticated: {request.user.is_authenticated}")
    if not hasattr(request.user, 'profile'):
        birth_date = date(2000, 1, 1)
        age = (timezone.now().date() - birth_date).days // 365
        print(f"No profile found for user: {request.user.username}, creating default")
        profile = Profile.objects.create(
            user=request.user,
            name=request.user.username,
            birth_date=birth_date,
            age=age,
            weight=0.0  # Default weight to satisfy NOT NULL
        )
        print(f"Default profile created for {request.user.username}: {profile.name}")
    else:
        profile = request.user.profile
        print(f"Profile found for {request.user.username}: {profile.name}")
    
    try:
        return render(request, 'core/my_account.html', {'profile': profile})
    except Exception as e:
        print(f"Error in my_account for {request.user.username}: {str(e)}")
        messages.error(request, f"Error loading account: {str(e)}")
        return redirect('home')

@login_required
def profile_list(request):
    profiles = Profile.objects.all()
    age_filter = request.GET.get('age')
    citizen_filter = request.GET.get('citizen')
    search = request.GET.get('search')
    if age_filter:
        profiles = profiles.filter(age__range=(int(age_filter.split('-')[0]), int(age_filter.split('-')[1])))
    if citizen_filter:
        profiles = profiles.filter(canada_us_citizen=citizen_filter)
    if search:
        profiles = profiles.filter(name__icontains=search)
    paginator = Paginator(profiles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/profile_list.html', {'page_obj': page_obj})

@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'core/profile_detail.html', {'profile': profile})

@login_required
def delete_account(request):
    if request.method == 'POST':
        try:
            user = request.user
            profile = user.profile
            profile.delete()
            user.delete()
            logout(request)
            messages.success(request, "Your account has been deleted successfully.")
            return redirect('home')
        except Profile.DoesNotExist:
            messages.error(request, "Profile not found.")
            return redirect('my_account')
        except Exception as e:
            messages.error(request, f"Error deleting account: {str(e)}")
            return redirect('my_account')
    return render(request, 'core/delete_account.html')

@login_required
def generate_biodata(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    
    # Create the HTTP response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{profile.name}_biodata.pdf"'
    
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=1*inch, bottomMargin=1*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Logo at the top (optional, adjust path as needed)
    logo_path = os.path.join('static', 'images', 'grca_logo.png')  # Replace with your logo path
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1*inch, height=1*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.2*inch))
    
    # Title
    title_style = styles['Heading1']
    title_style.alignment = 1  # Center alignment
    title_style.textColor = '#F89119'  # Orange
    title = Paragraph(f"{profile.name}'s Biodata", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Centered Profile Image
    image_path = profile.full_body_image.path if profile.full_body_image else os.path.join('static', 'images', 'default_full_body.jpg')
    if os.path.exists(image_path):
        profile_image = Image(image_path, width=3*inch, height=4*inch)
        profile_image.hAlign = 'CENTER'
        elements.append(profile_image)
    else:
        no_image = Paragraph("Image not available", styles['Normal'])
        no_image.hAlign = 'CENTER'
        elements.append(no_image)
    elements.append(Spacer(1, 0.5*inch))
    
    # Profile Data in Table Format
    data = [
        ["Field", "Details"],
        ["Name", profile.name],
        ["Email", request.user.email if request.user == profile.user else "N/A"],
        ["Phone", profile.phone_number or "Not specified"],
        ["About Yourself", profile.about_yourself or "Not specified"],
        ["Current Address", profile.current_address or "Not specified"],
        ["Gender", profile.get_gender_display() or "Not specified"],
        ["Birth Date", str(profile.birth_date) or "Not specified"],
        ["Age", str(profile.age) or "Not specified"],
        ["Marital Status", profile.get_marital_status_display() or "Not specified"],
        ["Canada/US Citizen", profile.get_canada_us_citizen_display() or "Not specified"],
        ["Visa Status", profile.visa_status or "Not specified"],
        ["Height", f"{profile.height} cm" if profile.height else "Not specified"],
        ["Weight", f"{profile.weight} kg" if profile.weight else "Not specified"],
        ["Birth Time", profile.birth_time or "Not specified"],
        ["Education", profile.education or "Not specified"],
        ["Occupation", profile.occupation or "Not specified"],
        ["Food Preference", profile.get_food_preference_display() or "Not specified"],
        ["City", profile.city or "Not specified"],
        ["State", profile.state or "Not specified"],
        ["Siblings", profile.siblings or "Not specified"],
        ["Native", profile.native or "Not specified"],
        ["Father's Name", profile.father_name or "Not specified"],
        ["Father's Native Place", profile.father_native or "Not specified"],
        ["Father's Phone Number", profile.father_number or "Not specified"],
        ["Father's Location", profile.father_location or "Not specified"],
        ["Father's Occupation", profile.father_occupation or "Not specified"],
        ["Father's Siblings", profile.father_siblings or "Not specified"],
        ["Father's Maternal Info", profile.father_maternal or "Not specified"],
        ["Grandfather's Name", profile.grandfather_name or "Not specified"],
        ["Grandmother's Name", profile.grandmother_name or "Not specified"],
        ["Mother's Name", profile.mother_name or "Not specified"],
        ["Mother's Father Name", profile.mother_father_name or "Not specified"],
        ["Mother's Maternal Info", profile.mother_maternal or "Not specified"],
    ]
    
    # Create the table
    table = Table(data, colWidths=[2.5*inch, 4.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#F89119'),  # Orange header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#FFF5E6'),  # Light orange background
        ('TEXTCOLOR', (0, 1), (-1, -1), '#AF6626'),  # Brown text
        ('GRID', (0, 0), (-1, -1), 1, '#AF6626'),  # Brown grid
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, '#AF6626'),
        ('BOX', (0, 0), (-1, -1), 2, '#F89119'),  # Thicker orange border
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    table.hAlign = 'CENTER'
    elements.append(table)
    
    # Add copyright notice at the bottom
    elements.append(Spacer(1, 0.5*inch))
    copyright_style = styles['Normal']
    copyright_style.alignment = 1  # Center alignment
    copyright_style.textColor = '#AF6626'  # Brown
    copyright = Paragraph("© GRCA Matrimony. All rights reserved.", copyright_style)
    elements.append(copyright)
    
    # Build the PDF
    doc.build(elements)
    return response