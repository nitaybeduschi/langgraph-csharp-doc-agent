## Fluxo do Agente

O grafo do agente usa validacao condicional do arquivo e, quando a entrada e valida,
dispara duas analises independentes em paralelo. Os resultados convergem em
`merge_analyses`, que valida e consolida os dados antes da geracao da documentacao.

```mermaid
flowchart TD
    Start((START)) --> load["load_source_file"]
    load --> router["should_continue_after_file_validation\n(router)"]
    router -- invalid --> finish["finish_with_error"]
    router -- valid --> fanout["start_parallel_analysis"]
    fanout --> structure["analyze_structure"]
    fanout --> security["audit_security_metrics"]
    structure --> merge["merge_analyses"]
    security --> merge
    merge --> validate_analysis["validate_analysis"]
    validate_analysis -- success --> gen["generate_documentation"]
    validate_analysis -- failure --> finish
    gen --> export["export_markdown"]
    export --> End((END))
```

Principais pontos:

- `CodeAnalysisResult` e `DocumentationOutput` sao schemas Pydantic `BaseModel`.
- `analyze_structure` extrai `class_name`, `methods` e `dependencies`.
- `audit_security_metrics` calcula metricas leves e riscos potenciais.
- `merge_analyses` faz o fan-in e grava o resultado consolidado em `extracted_info`.
- Em caso de falha nas validacoes, `finish_with_error` marca `success=False` e preserva `errors`.

Arquivos relevantes:

- `app/graph.py` - configuracao do grafo, fan-out e fan-in
- `app/schemas.py` - schemas Pydantic de analise e saida
- `app/nodes.py` - nos do workflow
- `app/routers.py` - roteadores de decisao
- `app/state.py` - definicao do `AgentState`
