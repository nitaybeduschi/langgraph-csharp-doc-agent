# LangGraph C# Documentation Agent

Agente inteligente em **LangGraph** para gerar documentacao tecnica em Markdown a partir de arquivos C#.

O projeto recebe um arquivo `.cs`, valida o caminho, sanitiza o conteudo contra prompt injection, extrai informacoes estruturais, gera documentacao com LLM ou fallback local, persiste checkpoints e pode exportar o resultado depois de aprovacao humana. Tambem expoe uma API FastAPI para acionamento por webhook e notificacao visual no Discord.

## Arquitetura

```text
app/
    api.py              # FastAPI webhook trigger e notificacao Discord
    config.py           # ambiente, provider de LLM e LangSmith
    graph.py            # montagem do grafo LangGraph
    logging_config.py   # logs JSON com trace_id
    main.py             # CLI
    nodes.py            # nos principais do workflow
    prompts.py          # prompts de documentacao
    qa.py               # revisao estatica opcional com IA
    routers.py          # roteamento condicional
    schemas.py          # modelos Pydantic
    security.py         # sanitizacao e path traversal guard
    state.py            # AgentState
    tools.py            # tools LangChain
docs/
    README.md
    arquitetura/
        flow.md
    evidencias/
        README.md
    prompts/
        01-estrutura-inicial-agent.md
        02-evolucao-graphs.md
        03-integracao-llm.md
        04-add-memory.md
        refinement.md
    qa/
        README.md
examples/
output/
scripts/
tests/
```

Componentes principais:

- CLI: `python -m app.main examples/sample_service.cs`
- API: `POST /webhooks/documentation`
- Grafo: `build_graph()` em `app/graph.py`
- LLM: `get_llm()` em `app/config.py`
- Persistencia: `SqliteSaver`
- Observabilidade: `structlog` JSON e LangSmith
- Qualidade: `ruff`, `mypy`, `pytest` e analisador de logs de CI

## Grafo LangGraph

O grafo usa `AgentState` como estado compartilhado. Ele valida a entrada, executa analises paralelas e consolida os dados antes da geracao.

Fluxo principal:

1. `load_source_file`
2. `should_continue_after_file_validation`
3. `start_parallel_analysis`
4. `analyze_structure` e `audit_security_metrics` em paralelo
5. `merge_analyses`
6. `validate_analysis`
7. `review_code_quality`, quando `include_qa_review=True`
8. `generate_documentation`
9. pausa HITL antes de `export_markdown`
10. `export_markdown`

O grafo e compilado com checkpoint SQLite e `interrupt_before=["export_markdown"]`, permitindo revisar a documentacao antes da escrita final. A API webhook resume automaticamente essa pausa para completar a execucao de ponta a ponta.

Veja o diagrama completo em [docs/arquitetura/flow.md](docs/arquitetura/flow.md).

## Tools/MCP

O projeto expoe tools LangChain em `app/tools.py`:

- `read_text_file_tool`
- `write_text_file_tool`

As tools usam schemas Pydantic (`ReadTextFileInput` e `WriteTextFileInput`) e passam pela validacao de workspace em `app/security.py`.

Nao ha servidor MCP dedicado neste repositorio ainda. A estrutura atual ja separa tools, schemas e seguranca, deixando o projeto pronto para publicar essas capacidades em um servidor MCP futuramente.

## Memoria/RAG

A memoria operacional do agente usa checkpoints SQLite via `SqliteSaver`. Cada execucao pode receber um `thread_id`, permitindo pausar e retomar o grafo.

Uso na CLI:

```bash
python -m app.main examples/sample_service.cs --thread-id demo-session
python -m app.main examples/sample_service.cs --thread-id demo-session --approve-export
```

Estado persistido:

- arquivo de entrada e saida
- codigo fonte e versao sanitizada
- analise estrutural
- metricas de seguranca
- documentacao gerada
- erros, warnings e `trace_id`

RAG vetorial ainda nao esta implementado. O ponto natural para evolucao e adicionar recuperacao de contexto antes de `generate_documentation`, alimentando o prompt com exemplos, padroes internos ou documentacao corporativa.

## Seguranca

O modulo `app/security.py` implementa duas defesas principais:

- Sanitizacao contra prompt injection no C# antes do envio ao LLM.
- Bloqueio de path traversal com `Path.resolve()` e verificacao de que entradas/saidas permanecem dentro do workspace.

O prompt tambem instrui o modelo a tratar o codigo fonte como dado nao confiavel, sem seguir instrucoes embutidas no arquivo.

Exemplos de entradas neutralizadas:

- delimitadores de prompt como cercas Markdown maliciosas
- labels como `system:`, `developer:` e `user:`
- instrucoes como `ignore previous instructions`

## Observabilidade

`app/logging_config.py` configura logs estruturados em JSON com:

- `trace_id`
- `node_name`
- `timestamp`
- `event`
- `level`

LangSmith e habilitado por padrao no runtime:

```env
LANGCHAIN_TRACING_V2=true
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
```

No CI, o tracing e desligado nos quality gates para evitar falhas de ingestao em ambiente sem credenciais.

## QA

O modulo `app/qa.py` adiciona um no opcional de revisao:

- `review_code_quality`

Ele gera sugestoes estaticas locais e, quando ha LLM disponivel, complementa com uma revisao em Markdown. O no e habilitado pela CLI com:

```bash
python -m app.main examples/sample_service.cs --qa-review
```

Tambem pode ser habilitado via API com `include_qa_review=true`.

## DevOps

O pipeline em `.github/workflows/ci.yml` executa:

- `python -m ruff check app tests scripts`
- `python -m mypy app`
- `python -m pytest -q`

O job falha quando lint, tipagem ou testes falham. Os logs de cada etapa sao capturados em `.ci-logs`.

Quando o build falha, o script `scripts/ai_log_analyzer.py` roda automaticamente para:

- ler logs de `ruff`, `mypy` e `pytest`
- calcular `risk_score`
- classificar o risco como `low`, `medium` ou `high`
- escrever um resumo no `GITHUB_STEP_SUMMARY`
- usar LLM quando disponivel, com fallback heuristico quando nao houver credenciais

## Low-Code

A API FastAPI permite disparar o agente por HTTP a partir de ferramentas Low-Code, automacoes ou GitHub Actions.

Suba a API localmente:

```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

Dispare a geracao:

```bash
curl -X POST http://127.0.0.1:8000/webhooks/documentation \
  -H "Content-Type: application/json" \
  -d '{"input_file":"examples/sample_service.cs","output_file":"output/webhook-doc.md","notify_discord":true}'
```

Payload aceito:

```json
{
  "input_file": "examples/sample_service.cs",
  "output_file": "output/webhook-doc.md",
  "thread_id": "optional-thread-id",
  "include_qa_review": false,
  "notify_discord": true,
  "discord_webhook_url": "optional-request-scoped-webhook"
}
```

Se `discord_webhook_url` nao for enviado, a API usa `DISCORD_WEBHOOK_URL` do ambiente.

A resposta inclui:

- `trace_id`
- `thread_id`
- `status`
- `output_file`
- `documentation_summary`
- `metrics`
- `notification_sent`
- `errors`
- `warnings`

## Configuracao

Crie um `.env` na raiz do projeto:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gemini-3.5-flash
LLM_PROVIDER=gemini
LANGCHAIN_TRACING_V2=true
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
```

Apesar do nome `OPENAI_API_KEY`, a aplicacao tambem aceita essa variavel como API key do Gemini por compatibilidade. Tambem e possivel usar `GOOGLE_API_KEY` ou `GEMINI_API_KEY`.

## Execucao Local

Instale as dependencias:

```bash
python -m pip install -r requirements.txt
```

Gere documentacao via CLI:

```bash
python -m app.main examples/sample_service.cs --output output/documentation.md
```

Execute com QA opcional:

```bash
python -m app.main examples/sample_service.cs --qa-review
```

## Testes

```bash
python -m ruff check app tests scripts
python -m mypy app
python -m pytest -q
```

Os testes usam mocks para evitar chamadas externas ao LLM e ao Discord.

## Exemplos

- Entrada: [examples/sample_service.cs](examples/sample_service.cs)
- Saida exemplo: [examples/output_sample_service.md](examples/output_sample_service.md)
- Saida via webhook local: [output/webhook-doc.md](output/webhook-doc.md)

## Evidencias e Prompts

- Indice tecnico da pasta `docs`: [docs/README.md](docs/README.md)
- Video demo: [https://youtu.be/bS5qZCqTu7k](https://youtu.be/bS5qZCqTu7k)
- Evidencias tecnicas de execucao, logs JSON, payloads webhook e falhas esperadas: [docs/evidencias/README.md](docs/evidencias/README.md)
- Ciclo de refinamento dos prompts, com tabela problema -> prompt alterado -> resultado: [docs/prompts/refinement.md](docs/prompts/refinement.md)
- Prompts historicos do desenvolvimento: [docs/prompts/](docs/prompts/)
- QA, testes inteligentes e risco: [docs/qa/README.md](docs/qa/README.md)

## Como Contribuir

1. Crie uma branch para sua alteracao.
2. Faca commits com mensagens semanticas.
3. Rode `ruff`, `mypy` e `pytest`.
4. Abra um pull request para `develop`.
