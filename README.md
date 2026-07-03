# Distribuidora de Bebidas em Alta Escala — Squad OO em Sistemas Reais

Este projeto foi desenvolvido para a disciplina de Orientação a Objetos. O objetivo principal é a aplicação de técnicas avançadas de modelagem, encapsulamento e proteção de regras de negócio em um domínio rico, sem o acoplamento a bancos de dados tradicionais.

A persistência do sistema é mockada utilizando arquivos JSON (`data/db.json`) com controle de semáforo para simular transações concorrentes de forma segura.

---

## 1. Requisitos do Sistema

- **Python 3.12+**
- Gerenciador de pacotes **pip**

---

## 2. Configuração e Instalação

1. Clone o repositório e acesse a branch da equipe:
   ```bash
   git checkout squadOOSistemasReais
   ```

2. Instale as dependências do projeto e as ferramentas de testes:
   ```bash
   pip install -r requirements.txt pytest pytest-django
   ```
   *(Nota: Se estiver utilizando um sistema com restrição de pacotes externos, utilize a flag `--user --break-system-packages` para instalar no escopo do usuário).*

---

## 3. Como Rodar os Testes Unitários

A branch possui uma suíte de testes robusta que valida o ciclo de vida do Pedido (Rascunho, Pendente, Aprovado, Separado, Expedido, Cancelado), regras de estoque com baixa física FEFO, usuários e permissões.

Para executar os testes:
```bash
python3 -m pytest tests/test_dominio.py
```

---

## 4. Como Executar a API e Acessar o Swagger UI

A API REST expõe todos os endpoints de controle logístico e administrativo. Para rodar o servidor:

```bash
python3 manage.py runserver
```

Assim que o servidor iniciar, abra o seu navegador e acesse a documentação interativa:
👉 **[http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)**

### Fluxo Recomendado de Testes na Interface:
1. Acesse o Swagger e localize o bloco **Auth**.
2. No endpoint `POST /api/auth/login/`, clique em **"Try it out"**, insira o login `"admin"` e a senha `"uid-admin-001"`, e clique em **"Execute"**.
3. Copie o `"token"` gerado na resposta JSON.
4. Clique no botão **"Authorize"** (cadeado) no topo da página, cole o token de texto e clique em **Authorize**.
5. Agora você pode testar todas as outras rotas administrativas e de domínio com a sua permissão autorizada!
