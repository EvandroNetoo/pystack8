from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.messages import constants

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .decorators import only_unauthenticated, only_authenticated


@only_unauthenticated(redirect_url='solicitar_exames')
def register(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            return render(request, 'register.html')
        
        case 'POST':
            primeiro_nome = request.POST.get('primeiro_nome')
            ultimo_nome = request.POST.get('ultimo_nome')
            username = request.POST.get('username')
            email = request.POST.get('email')
            senha = request.POST.get('senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            if '' in [x.strip() for x in request.POST.values()]:
                messages.add_message(request, constants.ERROR, 'Todos campos devem ser preenchidos.')
                return redirect('register')

            if not senha == confirmar_senha:
                messages.add_message(request, constants.ERROR, 'Senhas não coincidem.')
                return redirect('register')
            
            if len(senha) < 6:
                messages.add_message(request, constants.ERROR, 'Senha deve ter no mínimo 8 caracteres.')
                return redirect('register')
            
            try:
                user = User.objects.create_user(
                    first_name=primeiro_nome,
                    last_name=ultimo_nome,
                    username=username,
                    email=email,
                    password=senha,
                )
                messages.add_message(request, constants.SUCCESS, 'Usuário salvo com sucesso.')
                auth_login(request, user)
                return redirect('index')
            except: 
                messages.add_message(request, constants.ERROR, 'Erro interno do sistema, contate um administrador.')
                return redirect('register')
            

@only_unauthenticated(redirect_url='solicitar_exames')
def login(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            return render(request, 'login.html')
        
        case 'POST':
            username = request.POST.get('username')
            senha = request.POST.get('senha')

            user = authenticate(username=username, password=senha)

            if user:
                auth_login(request, user)
                return redirect('index')
            
            else:
                messages.add_message(request, constants.ERROR, 'Usuario ou senha inválidos.')
                return redirect('login')  


@login_required(login_url='login')
def logout(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            auth_logout(request)
            messages.add_message(request, constants.SUCCESS, 'Usuario desconectado com sucesso.')
            return redirect('login')
        
        case 'POST':
            pass