import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import SearchHistory


def fetch_forecast(city_name):
    api_key = settings.OPENWEATHERMAP_API_KEY
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric"

    forecast_data = []

    try:
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json().get('list', [])

        forecast_parsed = []
        for entry in forecast_data:
            date = entry['dt_txt']
            temp = entry['main']['temp']
            description = entry['weather'][0]['description']
            forecast_parsed.append({
                'date': date,
                'temp': temp,
                'description': description
            })
            if len(forecast_parsed) == 3:
                break

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except ValueError as e:
        print(f"JSON decoding failed: {e}")

    return forecast_parsed


@login_required
def history(request):

    user_history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'weather_app/history.html', {'history': user_history})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


def index(request):
    weather_data = None
    forecast_data = []
    previous_cities = request.session.get('previous_cities', [])

    if request.method == 'POST':
        city_name = request.POST.get('city')
        forecast_data = fetch_forecast(city_name)
        if city_name not in previous_cities:
            previous_cities.append(city_name)
            request.session['previous_cities'] = previous_cities

    elif request.GET.get('city'):
        city_name = request.GET.get('city')
        forecast_data = fetch_forecast(city_name)

    if request.GET.get('previous_city'):
        city_name = request.GET.get('previous_city')
        forecast_data = fetch_forecast(city_name)

    context = {
        'forecast_data': forecast_data,
        'previous_cities': previous_cities
    }

    return render(request, 'weather_app/index.html', context)


@require_GET
def city_autocomplete(request):
    term = request.GET.get('term', '')
    cities = SearchHistory.objects.filter(city__icontains=term).values_list('city', flat=True).distinct()
    return JsonResponse(list(cities), safe=False)
