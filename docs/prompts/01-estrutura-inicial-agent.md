# Objetivo

Crie a estrutura inicial de um projeto Python utilizando **LangGraph** para um agente de IA.

O projeto será um **C# Documentation Agent**, responsável por receber um arquivo `.cs`, analisar seu conteúdo e gerar documentação técnica em Markdown.

Neste momento, **não implemente toda a lógica do agente**. O objetivo é criar uma base organizada e extensível.

## Requisitos

Utilize:

- Python 3.12+
- LangGraph
- LangChain
- OpenAI
- Estrutura modular
- Boas práticas de organização

## Estrutura esperada

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

requirements.txt
```

## O que cada arquivo deve conter

### state.py

Criar o estado compartilhado do LangGraph utilizando `TypedDict`.

Inicialmente o estado deve possuir campos como:

- `input_file`
- `source_code`
- `extracted_info`
- `documentation`
- `output_file`
- `errors`

### graph.py

Criar o grafo principal utilizando `StateGraph`.

Mesmo que inicialmente exista apenas um fluxo simples, o código deve ficar preparado para adicionar novos nós posteriormente.

### nodes.py

Criar funções de nodes separadas para cada etapa do fluxo.

Inicialmente criar apenas stubs para:

- `load_source_file`
- `analyze_code`
- `generate_documentation`
- `export_markdown`

Cada função deve receber e retornar o estado.

### tools.py

Criar ferramentas reutilizáveis para:

- leitura de arquivos
- gravação de arquivos

Ainda não é necessário utilizar decorators do LangChain caso não sejam necessários.

### prompts.py

Criar um local centralizado para armazenar prompts do LLM.

Adicionar um prompt inicial para geração de documentação técnica de código C#.

### config.py

Centralizar:

- leitura da API key
- configuração do modelo
- constantes do projeto

### main.py

Criar um ponto de entrada que:

- receba o caminho de um arquivo `.cs`
- execute o grafo
- imprima o resultado

Ainda pode utilizar um exemplo fixo.

## Fluxo inicial

```text
Arquivo C#
  ↓
Load File
  ↓
Analyze Code
  ↓
Generate Documentation
  ↓
Export Markdown
```

## Implementação

Neste primeiro momento:

- implemente apenas a estrutura
- utilize implementações simples
- onde necessário, utilize TODOs
- documente o código
- adicione type hints
- deixe a arquitetura preparada para evolução

O código deve ser limpo, organizado e seguir boas práticas de Python.

Não implemente funcionalidades desnecessárias. O foco é construir uma boa fundação para evoluir o agente nas próximas etapas.
