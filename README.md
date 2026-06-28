# Proposta de camadas, fronteiras, infraestrutura e integrações.

## Proteção de domínio
O domínio será protegido ao estabelecer as regras de negócio somente nele, de forma independente das camadas de aplicação e infraestrutura.

Isso será realizado por meio de uma estrutura de pastas que delimita domínio, aplicação e infra, assim deixa explícito onde cada camada é implementada em código.

Além disso, aproveita-se dessa estrutura para implementar um linter, que verifica se a mesma está sendo respeitada. Por exemplo, nenhum arquivo dentro de src/domain/ pode importar de qualquer arquivo que não esteja dentro da pasta src/domain/

Por fim, a proteção do core domain também é feita por meio de **code-reviews** que verificam de forma manual se services, controllers e databases estão implementando regras de negócio que deveriam estar no domain.

## Determinção de fronteiras
Respeitando o princípio D de SOLID, *Dependency Inversion Principle*, as camadas externas dependem das camadas internas, e nunca o inverso. Assim, por exemplo, utiliza-se o padrão Repository, para estabelecer uma forma da database implementar as entities estabelecidas no domínio.

## Integrações externas
O uso de contratos estabelecidos no domínio permite a utilização de integrações externas enquanto protege domain de ficar acoplado ou ser contaminado por entidades externas. Assim, as integrações internas devem se adaptar ao que foi estabelecido no domain, não o contrário, assim o domínio não se importa em como de fato o contrato é aplicado, ele somente exige que ele implemente-o.

Para isso, utiliza-se implementações à nível de infraestrutura, por exemplo, com controllers, que façam uma adptação, ou filtragem, do conteúdo externo, para que chegue ao conteúdo interno somente o que é necessário e válido para seu funcionamento.