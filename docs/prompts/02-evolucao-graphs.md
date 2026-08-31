# Objetivo

Evoluir o workflow do agente LangGraph.

O projeto já possui um fluxo funcional com os nós:

- `load_source_file`
- `analyze_code`
- `generate_documentation`
- `export_markdown`

Atualmente o fluxo é totalmente linear.

Quero evoluí-lo para demonstrar melhor os recursos do LangGraph, mantendo a simplicidade do projeto.

## Fluxo atual

```text
load_source_file
  ↓
analyze_code
  ↓
generate_documentation
  ↓
export_markdown
```

## Objetivo da evolução

Adicionar validações e decisões utilizando arestas condicionais (`Conditional Edges`), tornando o fluxo mais próximo de um agente real.

## Fluxo desejado

```text
START
  ↓
load_source_file
  ↓
file validation router
  ├─ válido   → analyze_code
  └─ inválido → finish_with_error

analyze_code
  ↓
validate_analysis
  ├─ sucesso → generate_documentation
  └─ falha   → finish_with_error

generate_documentation
  ↓
export_markdown
  ↓
END
```

## Requisitos

Criar os seguintes novos nós ou roteadores:

### validate_source_file

Responsável por verificar:

- arquivo existe
- extensão é `.cs`
- conteúdo não está vazio

Caso alguma validação falhe:

- preencher `errors` no estado
- direcionar para `finish_with_error`

Observação: nesta implementação, a validação leve do arquivo foi feita como um router ligado a `load_source_file`, usando `should_continue_after_file_validation` em `app/routers.py`.

### validate_analysis

Após a análise do código, verificar se informações mínimas foram extraídas:

- nome da classe
- namespace, quando disponível
- pelo menos um método

Caso não seja possível gerar documentação de qualidade:

- registrar erro
- interromper o fluxo

### finish_with_error

Último nó responsável por:

- registrar mensagem amigável
- retornar o estado sem lançar exceções

## Estado

Evoluir o `AgentState` adicionando campos úteis como:

- `success`
- `errors`
- `warnings`

Mantendo compatibilidade com o restante do projeto.

## Graph

Modificar `build_graph()` para utilizar:

- `add_conditional_edges()` para roteamento condicional
- funções de roteamento em `app/routers.py`
- nós em `app/nodes.py`

Evitar lógica complexa dentro do próprio grafo.

## Boas práticas

- código limpo
- type hints
- funções pequenas
- comentários apenas quando agregarem valor
- preparado para futuras expansões, como memória, tools e human-in-the-loop

O objetivo não é aumentar a complexidade, mas demonstrar o uso adequado dos recursos do LangGraph em um fluxo realista.
