from django.urls import path
from .views import *

urlpatterns = [
    path('gerenciar_clientes/', gerenciar_clientes, name='gerenciar_clientes'),
    path('cliente/<int:cliente_id>', cliente, name='cliente'),
    path('exame_cliente/<int:exame_id>', exame_cliente, name="exame_cliente"),
    path('proxy_pdf/<int:exame_id>', proxy_pdf, name="proxy_pdf"),
    path('gerar_senha/<int:exame_id>', gerar_senha, name="gerar_senha"),
    path('alterar_dados_exame/<int:exame_id>', alterar_dados_exame, name="alterar_dados_exame"),
]