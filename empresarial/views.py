from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages
from authentication.decorators import only_staff
from django.http import FileResponse, HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Value
from django.db.models.functions import Concat
from empresarial.utils import gerar_pdf_exames, gerar_senha_aleatoria

from exams.models import SolicitacaoExame


@only_staff(redirect_url='solicitar_exames')
def gerenciar_clientes(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            clientes = User.objects.filter(is_staff=False)

            nome_completo = request.GET.get('nome')
            email = request.GET.get('email')

            if email:
                clientes = clientes.filter(email__contains = email)
            else:
                email = ''

            if nome_completo:
                clientes = clientes.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(full_name__contains=nome_completo)
            else:
                nome_completo = ''


            return render(request, 'gerenciar_clientes.html', {'clientes': clientes, 'nome_completo': nome_completo, 'email': email})
        
        case 'POST':
            pass


@only_staff(redirect_url='solicitar_exames')
def cliente(request: HttpRequest, cliente_id: int) -> HttpResponse:
    match request.method:
        case 'GET':
            cliente = User.objects.get(id=cliente_id)
            exames = SolicitacaoExame.objects.filter(usuario=cliente)
            return render(request, 'cliente.html', {'cliente': cliente, 'exames': exames})
                
        case 'POST':
            pass


@only_staff(redirect_url='solicitar_exames')
def exame_cliente(request: HttpRequest, exame_id: int) -> HttpResponse:
    match request.method:
        case 'GET':
            exame = SolicitacaoExame.objects.get(id=exame_id)
            return render(request, 'exame_cliente.html', {'exame': exame})
                
        case 'POST':
            pass


@only_staff(redirect_url='solicitar_exames')
def proxy_pdf(request: HttpRequest, exame_id: int) -> HttpResponse:
    match request.method:
        case 'GET':
            exame = SolicitacaoExame.objects.get(id=exame_id)

            response = exame.resultado.open()
            return FileResponse(response)
                
        case 'POST':
            pass


@only_staff(redirect_url='solicitar_exames')
def gerar_senha(request: HttpRequest, exame_id: int) -> HttpResponse:
    match request.method:
        case 'GET':
            exame = SolicitacaoExame.objects.get(id=exame_id)

            if exame.senha:
                # Baixar o documento da senha já existente
                return FileResponse(gerar_pdf_exames(exame.exame.nome, exame.usuario, exame.senha), filename="token.pdf")
            
            senha = gerar_senha_aleatoria(9)
            exame.senha = senha
            exame.save()
            return FileResponse(gerar_pdf_exames(exame.exame.nome, exame.usuario, exame.senha), filename="token.pdf")
                
        case 'POST':
            pass


@only_staff(redirect_url='solicitar_exames')
def alterar_dados_exame(request: HttpRequest, exame_id: int) -> HttpResponse:
    match request.method:
        case 'GET':
                pass
        case 'POST':
            exame = SolicitacaoExame.objects.get(id=exame_id)

            pdf = request.FILES.get('resultado')
            status = request.POST.get('status')
            requer_senha = request.POST.get('requer_senha')
            
            if requer_senha and (not exame.senha):
                messages.add_message(request, constants.ERROR, 'Para exigir a senha primeiro crie uma.')
                return redirect(f'/empresarial/exame_cliente/{exame_id}')
            
            exame.requer_senha = True if requer_senha else False

            if pdf:
                exame.resultado = pdf
                
            exame.status = status
            exame.save()
            messages.add_message(request, constants.SUCCESS, 'Alteração realizada com sucesso')
            return redirect(f'exame_cliente', exame_id)