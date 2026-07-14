# LangGraph C# Documentation Agent

Agente inteligente desenvolvido com **LangGraph** para automatizar a geração de documentação técnica de código C#.

## Objetivo

Este projeto foi desenvolvido como mini projeto avaliativo da disciplina de Agentes com IA.

O agente recebe um arquivo `.cs`, analisa seu conteúdo e gera uma documentação técnica inicial em Markdown, servindo como base para evoluções futuras.

## Status atual

✅ Estrutura inicial do projeto implementada.
✅ Fluxo básico do agente com LangGraph criado.
✅ Arquivo de exemplo em `examples/` disponível para testes.
✅ Testes unitários básicos implementados.

## Funcionalidades implementadas

- [x] Estrutura modular do projeto
- [x] Estado compartilhado para o workflow
- [x] Grafo inicial com nós de carregamento, análise, geração e exportação
- [x] Leitura de arquivo C# de exemplo
- [x] Geração de documentação inicial em Markdown
- [x] Testes unitários para a estrutura inicial

## Tecnologias

- Python 3.12+
- LangGraph
- LangChain
- OpenAI API
- Markdown
- pytest

## Estrutura do projeto

```text
app/
    __init__.py
    main.py
    graph.py
    state.py
    nodes.py
    tools.py
    prompts.py
    config.py
examples/
output/
docs/
prompts/
tests/
requirements.txt
```

## Diagrama do fluxo atualizado

Adicionamos validações leves e roteamento condicional ao grafo. Veja o diagrama
detalhado em `docs/flow.md`.

Resumo das melhorias:

- Validação de arquivo e leitura garantida antes da análise.
- Validação da análise para garantir informações mínimas (classe e métodos).
- Nó final `finish_with_error` para encerrar gracefully em caso de erros.

Veja `docs/flow.md` para o diagrama Mermaid e explicações.

## Como executar localmente

1. Instale as dependências:

```bash
$PYTHON -m pip install -r requirements.txt
```

2. Execute o projeto com um arquivo de exemplo:

```bash
$PYTHON -m app.main examples/sample_service.cs
```

3. O resultado será salvo em `output/documentation.md` por padrão.

## Como testar

```bash
$PYTHON -m pytest -q
```

## Como contribuir

1. Crie uma branch para sua alteração.
2. Faça commits com mensagens semânticas.
3. Abra um pull request para a branch `develop`.