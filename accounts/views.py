from django.shortcuts import render
from .forms import RegistrationForm

# Create your views here.

def register(request):
    form = RegistrationForm
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    return render(request, 'accounts/login.html')


def logout(request):
    return 
