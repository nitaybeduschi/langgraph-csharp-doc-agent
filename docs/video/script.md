# Roteiro do Video

Roteiro sugerido para uma gravacao de ate 10 minutos, cobrindo os criterios tecnicos do Modulo 2.

## 0:00 a 1:00 - Problema, Objetivo e Classificacao

**Tela sugerida:** abrir o `README.md` no topo e mostrar rapidamente `examples/sample_service.cs`.

**Fala:**

"Este projeto resolve um problema comum em times de desenvolvimento: transformar codigo C# em documentacao tecnica consistente, auditavel e pronta para revisao. A solucao e um agente com LangGraph que recebe um arquivo `.cs`, valida a entrada, sanitiza o conteudo contra prompt injection, extrai informacoes estruturais, gera documentacao em Markdown e permite aprovacao humana antes da exportacao final.

Classifico essa solucao como um agente de apoio ao ciclo de engenharia de software, com foco em documentacao, governanca e automacao DevOps. Ele nao substitui o desenvolvedor; ele acelera uma tarefa repetitiva e adiciona rastreabilidade, seguranca e qualidade ao processo."

**Evidencia para mostrar:**

- `README.md`
- `examples/sample_service.cs`
- `app/main.py`

## 1:00 a 2:00 - Arquitetura e Integracoes

**Tela sugerida:** abrir `docs/arquitetura/flow.md` e depois `app/graph.py`.

**Fala:**

"A arquitetura esta separada por responsabilidade. O grafo fica em `app/graph.py`, o estado tipado em `app/state.py`, os nodes em `app/nodes.py`, as rotas condicionais em `app/routers.py`, as ferramentas em `app/tools.py`, a seguranca em `app/security.py` e a API webhook em `app/api.py`.

O LangGraph coordena o fluxo, LangChain abstrai a chamada ao LLM, `structlog` gera logs JSON correlacionados por `trace_id`, `SqliteSaver` fornece memoria/checkpoint e FastAPI expoe o acionamento HTTP. Tambem ha integracao com Discord via webhook para notificar o termino da execucao."

**Evidencia para mostrar:**

- `docs/arquitetura/flow.md`
- `app/graph.py`
- `app/api.py`
- `app/logging_config.py`

## 2:00 a 3:00 - Cenario Principal

**Tela sugerida:** terminal com execucao via CLI.

**Comando sugerido:**

```bash
python -m app.main examples/sample_service.cs --output output/documentation.md --approve-export
```

**Fala:**

"No fluxo principal, eu executo o agente apontando para um arquivo C#. O primeiro node carrega e valida o arquivo. Em seguida, o grafo inicia uma etapa paralela: um ramo extrai a estrutura do codigo, como classe, metodos e dependencias; o outro calcula metricas e riscos simples de seguranca. Depois, o node `merge_analyses` consolida os resultados e o grafo valida se a analise e suficiente para gerar documentacao.

Na etapa seguinte, o agente monta um prompt seguro, envia ao LLM quando configurado e usa fallback local quando o provider nao esta disponivel. Por fim, a documentacao e exportada para Markdown."

**Evidencia para mostrar:**

- saida no terminal
- `output/documentation.md`
- logs JSON com `trace_id`

## 3:00 a 4:00 - Cenario de Risco ou Falha

**Tela sugerida:** mostrar `docs/evidencias/README.md`, secao de falhas, e `app/security.py`.

**Fala:**

"Agora demonstro um cenario de risco. O projeto trata duas classes de entrada adversarial: path traversal e prompt injection. Para path traversal, caminhos como `../secrets.env` sao resolvidos com `Path.resolve()` e comparados contra o workspace permitido. Se o caminho sair da raiz do projeto, a execucao e bloqueada antes de ler ou escrever arquivos.

Para prompt injection, o codigo C# e tratado como dado nao confiavel. Antes de enviar ao LLM, o conteudo passa por sanitizacao que neutraliza delimitadores maliciosos, labels de role como `system:` ou `developer:` e instrucoes como `ignore previous instructions`. Assim, comentarios dentro do codigo nao conseguem redefinir o comportamento do agente."

**Evidencia para mostrar:**

- `app/security.py`
- teste relacionado em `tests/test_nodes.py`
- exemplos em `docs/evidencias/README.md`

## 4:00 a 5:00 - Seguranca, Bloqueio e Aprovacao Humana

**Tela sugerida:** mostrar `build_graph()` e execucao com `thread_id`.

**Comandos sugeridos:**

```bash
python -m app.main examples/sample_service.cs --thread-id demo-video
python -m app.main examples/sample_service.cs --thread-id demo-video --approve-export
```

**Fala:**

"Alem da protecao de entrada, existe um limite de autonomia. Na CLI, o grafo e compilado com checkpoint SQLite e interrupcao antes de `export_markdown`. Isso cria uma etapa human-in-the-loop: o agente pode gerar a documentacao, mas a escrita final pode depender de aprovacao explicita.

Na primeira execucao, o fluxo pausa antes da exportacao. Na segunda, usando o mesmo `thread_id` e a flag `--approve-export`, o grafo retoma o checkpoint e conclui a escrita. Isso demonstra memoria operacional, rastreabilidade e controle humano sobre uma acao persistente."

**Evidencia para mostrar:**

- `app/graph.py`
- `app/main.py`
- arquivo de saida criado apenas apos aprovacao

## 5:00 a 6:00 - Evidencia de QA

**Tela sugerida:** rodar testes e mostrar `app/qa.py`.

**Comandos sugeridos:**

```bash
python -m ruff check app tests scripts
python -m mypy app
python -m pytest -q
python -m app.main examples/sample_service.cs --qa-review --approve-export
```

**Fala:**

"A camada de QA aparece em dois pontos. Primeiro, o projeto possui testes automatizados para grafo, nodes, seguranca, API e QA. Segundo, existe um node opcional chamado `review_code_quality`, implementado em `app/qa.py`. Ele gera sugestoes estaticas locais e pode complementar com revisao via LLM quando credenciais estiverem disponiveis.

Isso conecta IA ao processo de qualidade: o agente nao apenas gera documentacao, mas tambem pode apontar riscos de refatoracao, legibilidade e manutencao no codigo analisado."

**Evidencia para mostrar:**

- `tests/`
- `app/qa.py`
- `docs/qa/README.md`

## 6:00 a 8:00 - Pipeline, Logs, Anomalias e Risco

**Tela sugerida:** abrir `.github/workflows/ci.yml` e `scripts/ai_log_analyzer.py`.

**Fala:**

"No DevOps, o GitHub Actions executa quality gates obrigatorios: lint com Ruff, tipagem com MyPy e testes com Pytest. O pipeline falha se qualquer etapa encontrar erro, garantindo que problemas de estilo, tipo ou comportamento nao avancem silenciosamente.

Quando ocorre falha, os logs sao coletados em `.ci-logs` e o script `scripts/ai_log_analyzer.py` e executado automaticamente. Ele le os logs de `ruff`, `mypy` e `pytest`, identifica sinais de anomalia, calcula uma pontuacao de risco de zero a cem e classifica o resultado como baixo, medio ou alto. Se houver LLM configurado, o diagnostico e enriquecido por IA; se nao houver, o fallback heuristico ainda produz um resumo explicativo.

Esse ponto e importante porque transforma uma falha bruta de build em uma saida observavel e interpretavel. Em vez de apenas dizer que o CI falhou, o workflow mostra quais areas parecem mais arriscadas e ajuda a priorizar a correcao."

**Evidencia para mostrar:**

- `.github/workflows/ci.yml`
- `scripts/ai_log_analyzer.py`
- `docs/evidencias/README.md`
- exemplo de `GITHUB_STEP_SUMMARY`

**Comando opcional:**

```bash
python scripts/ai_log_analyzer.py --logs-dir .ci-logs
```

## 8:00 a 9:00 - Automacao Low-Code/No-Code

**Tela sugerida:** subir API local e chamar endpoint via curl/Postman/Insomnia.

**Comandos sugeridos:**

```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

```bash
curl -X POST http://127.0.0.1:8000/webhooks/documentation \
  -H "Content-Type: application/json" \
  -d '{"input_file":"examples/sample_service.cs","output_file":"output/webhook-doc.md","include_qa_review":true,"notify_discord":true}'
```

**Fala:**

"A automacao low-code aparece pelo endpoint FastAPI `POST /webhooks/documentation`. Ele permite que GitHub Actions, ferramentas de automacao ou plataformas low-code disparem o agente via HTTP. O payload define arquivo de entrada, saida, revisao de QA e notificacao.

Ao final da execucao, a API retorna status, metricas, resumo da documentacao e informacao sobre envio da notificacao. Se `DISCORD_WEBHOOK_URL` estiver configurado, o projeto envia um embed visual para Discord com o status da geracao, metricas principais e arquivo produzido."

**Evidencia para mostrar:**

- `app/api.py`
- resposta JSON do endpoint
- mensagem no Discord
- `output/webhook-doc.md`

## 9:00 a 10:00 - Limitacoes e Melhorias Futuras

**Tela sugerida:** abrir README nas secoes Memoria/RAG e Tools/MCP.

**Fala:**

"As principais limitacoes atuais sao intencionais e estao documentadas. Ainda nao ha RAG vetorial com chunking, indexacao e recuperacao semantica; a memoria atual e operacional, baseada em checkpoints SQLite. Tambem ainda nao existe um servidor MCP dedicado, embora as tools ja estejam separadas com schemas Pydantic e validacao de seguranca, o que facilita essa evolucao.

Como melhorias futuras, eu priorizaria tres frentes: primeiro, implementar RAG para lidar melhor com arquivos C# grandes e padroes internos de arquitetura; segundo, publicar as tools como servidor MCP; terceiro, ampliar as metricas de QA para gerar tendencias historicas de falha por modulo ou tipo de erro.

Com isso, o projeto demonstra os pilares principais do modulo: LangGraph com estado tipado, roteamento condicional, paralelismo simples, seguranca, observabilidade, QA com IA, DevOps inteligente, automacao via webhook e documentacao organizada para avaliacao."

**Evidencia para mostrar:**

- `README.md`
- `docs/README.md`
- `docs/evidencias/README.md`
- `docs/prompts/refinement.md`

## Checklist de Gravacao

- Mostrar problema e exemplo C# real.
- Mostrar diagrama do grafo.
- Executar fluxo principal.
- Mostrar falha ou defesa de seguranca.
- Demonstrar aprovacao humana/checkpoint.
- Rodar ou mostrar evidencias de QA.
- Abrir CI e analisador de logs.
- Demonstrar webhook e Discord.
- Fechar com limitacoes e proximos passos.
