from django.http import HttpRequest
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants


def only_authenticated(redirect_url):
    def decorator(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            
            if request.user.is_authenticated:
                if request.user.is_staff:
                    messages.add_message(request, constants.WARNING, 'É necessario ser um usuário comum para acessar esta página.')
                    return redirect('gerenciar_clientes')
                
                return view_func(request, *args, **kwargs)
            
            messages.add_message(request, constants.WARNING, 'É necessario estar logado para acessar esta página.')
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def only_staff(redirect_url):
    def decorator(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            messages.add_message(request, constants.WARNING, 'É necessario ser staff para acessar esta página.')
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def only_unauthenticated(redirect_url):
    def decorator(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            
            if request.user.is_authenticated:
                messages.add_message(request, constants.WARNING, 'É necessario estar deslogado para acessar esta página.')
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

