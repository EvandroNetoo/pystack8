from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from authentication.decorators import only_authenticated
from django.db.models import Sum
from django.contrib.messages import constants
from django.contrib import messages

from .models import AcessoMedico, TipoExame, PedidoExames, SolicitacaoExame

from datetime import date, datetime


@only_authenticated(redirect_url='login')
def solicitar_exames(request: HttpRequest) -> HttpResponse:
    tipos_exames = TipoExame.objects.all().order_by('nome')
    match request.method:
        case 'GET':
            return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames})

        case 'POST':
            exames_solicitados = request.POST.getlist('exames')
            solicitacao_exames = TipoExame.objects.filter(
                id__in=exames_solicitados)

            solicitacao_exames_disponiveis = solicitacao_exames.filter(
                disponivel=True)
            preco_total = solicitacao_exames_disponiveis.aggregate(total=Sum('preco'))[
                'total']

            return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames,
                                                             'solicitacao_exames': solicitacao_exames,
                                                             'preco_total': f'R$ {preco_total:.2f}'.replace('.', ',') if preco_total is not None else 'R$ 0,00  ',
                                                             'data': date.today().strftime(r'%d/%m/%Y')
                                                             })


@only_authenticated(redirect_url='login')
def fechar_pedido(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            pass
        case 'POST':
            exames_id = request.POST.getlist('exames')

            pedido_exame = PedidoExames(
                usuario=request.user,
                data=datetime.today(),
            )
            pedido_exame.save()

            solicitacao_exames = TipoExame.objects.filter(id__in=exames_id)
            for exame in solicitacao_exames:
                exame_temp = SolicitacaoExame(
                    usuario=request.user,
                    exame=exame,
                    status='E',
                )
                exame_temp.save()
                pedido_exame.exames.add(exame_temp)

            pedido_exame.save()
            messages.add_message(request, constants.SUCCESS,
                                 'Pedido de exame realizado com sucesso.')
            return redirect('gerenciar_pedidos')


@only_authenticated(redirect_url='login')
def gerenciar_pedidos(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            pedidos_exames = PedidoExames.objects.filter(usuario=request.user)
            return render(request, 'gerenciar_pedidos.html', {'pedidos_exames': pedidos_exames})
        case 'POST':
            pass


@only_authenticated(redirect_url='login')
def cancelar_pedido(request: HttpRequest, pedido_id: int) -> HttpResponse:
    match request.method:
        case 'GET':
            pedido = get_object_or_404(PedidoExames, id=pedido_id)

            if not pedido.usuario == request.user:
                messages.add_message(
                    request, constants.ERROR, 'O pedido acessado não é seu.')
                return redirect('gerenciar_pedidos')

            pedido.agendado = False
            pedido.save()
            messages.add_message(request, constants.SUCCESS,
                                 'Pedido excluído com sucesso.')
            return redirect('gerenciar_pedidos')

        case 'POST':
            pass


@only_authenticated(redirect_url='login')
def gerenciar_exames(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            exames = SolicitacaoExame.objects.filter(usuario=request.user)
            return render(request, 'gerenciar_exames.html', {'exames': exames})

        case 'POST':
            pass


@only_authenticated(redirect_url='login')
def permitir_abrir_exame(request: HttpRequest, exame_id: int) -> HttpResponse:
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if not exame.usuario == request.user:
        messages.add_message(request, constants.ERROR,
                             'O exame acessado não é seu.')
        return redirect('gerenciar_exames')

    match request.method:
        case 'GET':

            if exame.resultado == '':
                messages.add_message(
                    request, constants.ERROR, 'O exame não há um resultado anexado, contate o laboratório.')
                return redirect('gerenciar_exames')

            if not exame.requer_senha:

                return redirect(exame.resultado.url)

            else:
                return redirect(f'solicitar_senha_exame', exame.id)

        case 'POST':
            pass


@only_authenticated(redirect_url='login')
def solicitar_senha_exame(request: HttpRequest, exame_id: int) -> HttpResponse:
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if not exame.usuario == request.user:
        messages.add_message(request, constants.ERROR,
                             'O exame acessado não é seu.')
        return redirect('gerenciar_exames')

    match request.method:
        case 'GET':
            return render(request, 'solicitar_senha_exame.html', {'exame': exame})

        case 'POST':
            senha = request.POST.get("senha")
            if senha == exame.senha:
                return redirect(exame.resultado.url)
            else:
                messages.add_message(
                    request, constants.ERROR, 'Senha inválida')
                return redirect(f'solicitar_senha_exame', exame.id)


@only_authenticated(redirect_url='login')
def gerar_acesso_medico(request: HttpRequest) -> HttpResponse:
    match request.method:
        case 'GET':
            acessos_medicos = AcessoMedico.objects.filter(
                usuario=request. user)
            return render(request, 'gerar_acesso_medico.html', {'acessos_medicos': acessos_medicos})
        case 'POST':
            identificacao = request.POST.get('identificacao')
            tempo_de_acesso = request.POST.get('tempo_de_acesso')
            data_exame_inicial = request.POST.get("data_exame_inicial")
            data_exame_final = request.POST.get("data_exame_final")

            acesso_medico = AcessoMedico(
                usuario=request.user,
                identificacao=identificacao,
                tempo_de_acesso=tempo_de_acesso,
                data_exames_iniciais=data_exame_inicial,
                data_exames_finais=data_exame_final,
                criado_em=datetime.now()
            )

            acesso_medico.save()

            messages.add_message(request, constants.SUCCESS,
                                 'Acesso gerado com sucesso')
            return redirect('gerar_acesso_medico')


def acesso_medico(request: HttpRequest, token: str) -> HttpResponse:
    acesso_medico = get_object_or_404(AcessoMedico, token=token)
    if acesso_medico.status == 'Expirado':
        messages.add_message(request, constants.WARNING, 'Este link de acesso foi expirado, solicite outro.')
        return redirect('login')
    
    match request.method:
        case 'GET':
            pedidos = PedidoExames.objects.filter(usuario=acesso_medico.usuario,
                                                  data__gte=acesso_medico.data_exames_iniciais,
                                                  data__lte=acesso_medico.data_exames_finais,
                                                  )
            return render(request, 'acesso_medico.html', {'pedidos': pedidos})
        case 'POST':
            pass
