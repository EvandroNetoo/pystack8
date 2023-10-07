from django.urls import path
from .views import *

urlpatterns = [
    path('solicitar_exames/', solicitar_exames, name='solicitar_exames'),
    path('fechar_pedido/', fechar_pedido, name='fechar_pedido'),
    path('gerenciar_pedidos/', gerenciar_pedidos, name="gerenciar_pedidos"),
    path('cancelar_pedido/<int:pedido_id>', cancelar_pedido, name="cancelar_pedido"),
    path('gerenciar_exames/', gerenciar_exames, name="gerenciar_exames"),
    path('permitir_abrir_exame/<int:exame_id>', permitir_abrir_exame, name="permitir_abrir_exame"),
    path('solicitar_senha_exame/<int:exame_id>', solicitar_senha_exame, name="solicitar_senha_exame"),
    path('gerar_acesso_medico/', gerar_acesso_medico, name="gerar_acesso_medico"),
    path('acesso_medico/<str:token>', acesso_medico, name="acesso_medico"),
]
