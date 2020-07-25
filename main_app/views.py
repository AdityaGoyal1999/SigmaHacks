from django.shortcuts import render
from django.http import HttpResponse
import requests
from .models import User, Property, Image
from django.core.files.storage import FileSystemStorage
import os

# Create your views here.

def home(request):
    return render(request, template_name="main_app/index.html", context={'logout': "no",})

def platform_info(request):
    return render(request, template_name="main_app/platformInfo.html", context={"logout": "no",})

def covid_info(request):
    return render(request, template_name="main_app/covidInfo.html", context={"logout": "no",})

def login_page(request):
    context = {
        'login': True,
        'logout': "no",
    }
    return render(request, template_name="main_app/login.html", context=context)

def signup_page(request):
    context = {
        'login': False,
        "logout": "no",
    }
    return render(request, template_name="main_app/login.html", context=context)

def create_account(request):

    email = request.POST.get('unregisteredEmail')
    name = request.POST.get('name')
    password = request.POST.get('password')
    category = request.POST.get('category')

    if User.objects.filter(email=email).first() is None:
        # works
        user = User.objects.create(name=name, email=email, password=password, category=category)
        context = {
            'login': True,
            'message': 'Account created successfully. Now login.',
        }
        return render(request, template_name='main_app/login.html', context=context)
    else:
        # user exists
        context = {
            'login': False,
            'message': 'Account already exists',
            'logout': "no",
        }
        return render(request, template_name='main_app/login.html', context=context)



def login(request):

    email = request.POST.get('email')
    password = request.POST.get('password')

    user = User.objects.filter(email=email, password=password).first()
    if user is None:
        context = {
            'login': True,
            'message': 'Username or Password are wrong.',
        }
        return render(request, template_name='main_app/login.html', context=context)

    request.session['email'] = email
    props = []
    if user.category != 'warrior':
        props = Property.objects.filter(owner=email).all()


    return render(request, template_name='main_app/dashboard.html', context={'category': user.category, 'properties': props,})


def search_result(request):
    search = request.POST.get('search')
    # TODO: Search for the other props

    props = Property.objects.all()
    matching_properties = []
    for prop in props:
        if search in prop.number_and_street or search in prop.city or search in prop.state or search in prop.country:
            matching_properties.append(prop)

    context = {
        'search': search,
        'properties': matching_properties,
    }
    return render(request, 'main_app/searchResults.html', context=context)


def add_property(request):

    return render(request, template_name='main_app/addProperty.html')

def save_property(request):
    owner = request.session['email']
    street = request.POST.get('street')
    city = request.POST.get('city')
    state = request.POST.get('state')
    pincode = request.POST.get('pincode')
    country = request.POST.get('country')
    photo = request.FILES.get('image')
    rent = request.POST.get('rent')
    notes = request.POST.get('notes')
    if rent == '' or rent is None:
        rent = 0.0
    else:
        rent = float(rent)

    prop = Property.objects.create(owner=owner,number_and_street=street, pincode=pincode, city=city, state=state, country=country, rent=rent, notes=notes)
    img = Image.objects.create(post=prop, photo=photo)

    loc = "media/{}/{}/".format(request.session['email'], prop.pk)
    fs = FileSystemStorage(location=loc)
    if photo is not None:
        try:
            list_of_images = os.listdir(loc)
            if list_of_images == []:
                filename = fs.save("one.png", photo)
            else:
                filename = fs.save(photo.name, photo)
        except FileNotFoundError:
            filename = fs.save("one.png", photo)
        uploaded_file_url = fs.url(filename)
        

    path = "{}/media/{}/{}/".format(os.getcwd(), request.session['email'], prop.pk)
    img_list =os.listdir(path)

    # TODO: Change this IMMEDIATELY
    # return render(request, 'main_app/dashboard.html', context={"image_names": img_list, "email": request.session['email'],})
    user = User.objects.filter(email=request.session['email']).first()
    props = Property.objects.filter(owner=request.session['email']).all()

    return render(request, template_name='main_app/dashboard.html', context={'category': user.category, 'properties': props, "message": "Your property was added!",})

def single_property(request, pk):

    prop = Property.objects.get(pk=pk)
    email = prop.owner
    
    path = "{}/media/{}/{}/".format(os.getcwd(), email, pk)
    img_list =os.listdir(path)
    
    
    
    return render(request, 'main_app/singleProperty.html', context={"image_names": img_list, "email": email, "property": prop, "key": pk})



def logout(request):
    
    request.session.flush()
    return render(request, template_name="main_app/index.html", context={"logout": "no",})