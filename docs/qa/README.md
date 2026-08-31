# QA, Testes Inteligentes e Risco

Esta area documenta as evidencias de qualidade do projeto, conectando testes automatizados, revisao por IA e analise de risco no CI.

## Testes Automatizados

Comandos usados localmente e no GitHub Actions:

```bash
python -m ruff check app tests scripts
python -m mypy app
python -m pytest -q
```

Cobertura funcional demonstrada:

- compilacao e execucao do grafo LangGraph
- validacao de checkpoint e retomada por `thread_id`
- execucao opcional do no `review_code_quality`
- sanitizacao de prompt injection antes do LLM
- bloqueio de path traversal
- exportacao Markdown
- endpoint FastAPI e notificacao Discord mockada

## Revisao por IA

O no opcional `review_code_quality`, implementado em `app/qa.py`, executa revisao estatica local e pode complementar o diagnostico com LLM quando houver credenciais.

Acionamento via CLI:

```bash
python -m app.main examples/sample_service.cs --qa-review
```

Acionamento via webhook:

```json
{
  "input_file": "examples/sample_service.cs",
  "output_file": "output/webhook-doc.md",
  "include_qa_review": true,
  "notify_discord": true
}
```

## Analise de Risco no CI

O script `scripts/ai_log_analyzer.py` roda quando algum quality gate falha no GitHub Actions. Ele le os logs capturados, calcula `risk_score`, classifica o risco e escreve um resumo explicativo no `GITHUB_STEP_SUMMARY`.

Execucao local:

```bash
python scripts/ai_log_analyzer.py --logs-dir .ci-logs
```

Saida esperada:

```text
Risk level: low|medium|high
Risk score: 0-100
Summary: ...
```

## Evidencias Relacionadas

- [Evidencias tecnicas](../evidencias/README.md)
- [Refinamento de prompts](../prompts/refinement.md)
