from django.shortcuts import redirect, render
from django.http import HttpResponse
# from users.forms import LoginForm, RegisterForm

# Create your views here.
def home(request):
    return render(request, 'users/dashboard.html')


def login_view(request):
#     if request.method == 'POST':
#        form = LoginForm(request.POST)
#        if form.is_valid:
#            form.save()
#            return redirect('home')
#     else:       
#         form = LoginForm  
    return render(request, 'users/login.html', {'form': form})


# def register_view(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = RegisterForm
#     return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    return redirect('home')

def student_dashboard(request):
    return render('users/dashboard.html')

def lecturer_dashboard(request):
    return render(request, 'users/dashboard.html')