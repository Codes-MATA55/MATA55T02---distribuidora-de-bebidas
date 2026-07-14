Alguns insights que tivemos

Bebida._post_init_ -> volume negativo, preço negativo, nome vazio
suco._post_init_ -> percentual de polpa
itempedido._post_init_ -> quantidade zero ou negativa
estoque.entrada/saida -> quantidade negativa, saldo insuficiente

transições válidas:
criado -> emseparacao -> separado -> emexpedicao -> entregue
criado -> cancelado, emseparacao -> cancelado

transições inválidas
qualquer outra combinação lança um transicaodeestadoinvalidaeception

test_estados.py → cobre todas as transições
test_estoque.py → cobre invariantes do estoque
test_bebidas_e_observers.py → cobre invariantes das bebidas
test_separacao_expedicao.py → cobre fluxo completo

Revisão de responsabilidades

Pedido gerencia ciclo de vida
Estoque gerencia inventário
FIFOSeparacao decide como separar
ValidadorExpedicao decide se pode expedir
Cada estado sabe suas próprias transições
