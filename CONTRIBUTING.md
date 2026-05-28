## Regras de Código e Padrões de Commit

Nosso projeto segue o padrão oficial de desenvolvimento Python (PEP 8), que será fiscalizado automaticamente pelo linter Flake8.

O fluxo do projeto deve seguir a seguinte ordem: branch-equipe -> homologacao -> main

Para manter o histórico do projeto organizado, todas as mensagens de commit devem seguir este formato de texto:

`tipo(nomeSobrenome): descrição`

- **`tipo`**: Indica a intenção da mudança (se é um recurso novo, uma correção, etc.).
- **`nomeSobrenome` :**  Identificação do aluno responsável pelo commit.
- **`descrição`**: Um resumo curto do que foi feito, imperativo (ex: "adiciona", "corrige", "remove") e sem ponto final.

---

### Principais Tipos

- **feat**: Quando você adiciona uma função nova no sistema.
    - *Exemplo:* `feat(joao-silva): adiciona tela de login`
- **fix**: Quando você corrige um erro ou bug.
    - *Exemplo:* `fix(joao-silva): corrige conexao com mysql`
- **refactor**: Quando você limpa ou melhora um código existente (sem mudar o que ele faz).
    - *Exemplo:* `refactor(joao-silva): divide funcao gigante`
- **style**: Quando altera apenas formatação, espaços ou estilo visual.
    - *Exemplo:* `style(joao-silva): corrige espacamentos`
- **chore**: Quando mexe em configurações, instalação de pacotes ou arquivos do Git.
    - *Exemplo:* `chore(joao-silva): adiciona plugins no requirements`
- **docs**: Quando altera documentações ou textos do README.
    - *Exemplo:* `docs(joao-silva): atualiza instrucoes do projeto`

---

### Regras Rápidas

- Escreva a descrição sempre em letras minúsculas.
- Use verbos diretos no presente (adiciona, corrige, remove).
- Não coloque ponto final no término da frase.
- Não use commits genéricos como "ajustes" ou "testando".
- Use commits diferentes para cada alteração diferente feita.
