from django.contrib import admin
from .models import TipoExame, PedidoExames, SolicitacaoExame, AcessoMedico

admin.site.register(TipoExame)
admin.site.register(PedidoExames)
admin.site.register(SolicitacaoExame)
admin.site.register(AcessoMedico)