# LangGraph C# Documentation Agent

Agente inteligente desenvolvido com **LangGraph** para automatizar a geracao de documentacao tecnica de codigo C# em Markdown.

## Objetivo

Este projeto foi desenvolvido como mini projeto avaliativo da disciplina de Agentes com IA.

O agente recebe um arquivo `.cs`, analisa seu conteudo e gera uma documentacao tecnica inicial em Markdown. A geracao pode usar um LLM configurado em `app/config.py`; quando o LLM esta indisponivel, a aplicacao gera um fallback local simples.

## Status atual

- [x] Estrutura inicial do projeto implementada
- [x] Fluxo basico do agente com LangGraph criado
- [x] Arquivos de exemplo em `examples/` disponiveis para testes
- [x] Validacoes leves e roteamento condicional no grafo
- [x] Integracao com LLM para geracao de documentacao
- [x] Suporte a Gemini via API key no `.env`
- [x] Testes unitarios com mock do LLM

## Funcionalidades implementadas

- Estrutura modular do projeto
- Estado compartilhado para o workflow
- Grafo com nos de carregamento, analise, validacao, geracao e exportacao
- Leitura de arquivo C# de exemplo
- Analise basica para identificar classe e metodos publicos
- Prompt estruturado para documentacao tecnica
- Geracao de documentacao com LLM
- Fallback local quando o LLM falha ou fica indisponivel
- Testes unitarios sem chamada externa ao LLM

## Tecnologias

- Python 3.12+
- LangGraph
- LangChain
- Gemini API
- python-dotenv
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

## Configuracao do LLM

Crie um arquivo `.env` na raiz do projeto. Voce pode usar `.env.example` como referencia:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gemini-3.5-flash
LLM_PROVIDER=gemini
```

Apesar do nome `OPENAI_API_KEY`, a aplicacao tambem usa essa variavel como API key do Gemini para manter compatibilidade com a configuracao anterior. Tambem e possivel usar `GOOGLE_API_KEY` ou `GEMINI_API_KEY`.

A selecao do provedor fica isolada em `app/config.py`, na funcao `get_llm()`. O restante da aplicacao chama apenas essa fabrica e nao conhece diretamente o provedor usado.

Se a chamada ao Gemini falhar, por exemplo por indisponibilidade temporaria da API, o estado recebe o erro em `errors` e a documentacao gerada inclui:

```text
_Note: LLM unavailable or errored; this is a fallback._
```

## Como executar localmente

1. Instale as dependencias:

```bash
python -m pip install -r requirements.txt
```

2. Configure o `.env`:

```bash
cp .env.example .env
```

No Windows PowerShell, se preferir:

```powershell
Copy-Item .env.example .env
```

Depois edite `.env` e preencha a API key.

3. Execute o projeto com um arquivo de exemplo:

```bash
python -m app.main examples/sample_service.cs
```

4. Para escolher o arquivo de saida:

```bash
python -m app.main examples/customer-service.cs --output output/customer-service.md
```

O resultado sera salvo em `output/documentation.md` por padrao, ou no caminho passado em `--output`.

## Como testar

```bash
python -m pytest -q
```

Os testes unitarios usam mock para o LLM. Eles nao devem fazer chamadas para Gemini ou qualquer outro provedor externo. A comunicacao real com LLM deve acontecer apenas ao executar a aplicacao.

## Diagrama do fluxo atualizado

Adicionamos validacoes leves e roteamento condicional ao grafo. Veja o diagrama detalhado em `docs/flow.md`.

Resumo do fluxo:

- Validacao de arquivo e leitura garantida antes da analise
- Analise basica para extrair informacoes estruturadas
- Validacao da analise para garantir informacoes minimas
- Geracao de documentacao via LLM ou fallback local
- Exportacao do Markdown
- No final `finish_with_error` para encerrar gracefully em caso de erros

## Como contribuir

1. Crie uma branch para sua alteracao.
2. Faca commits com mensagens semanticas.
3. Abra um pull request para a branch `develop`.
