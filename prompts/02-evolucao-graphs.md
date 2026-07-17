# Objetivo

Evoluir o workflow do agente LangGraph.

O projeto já possui um fluxo funcional com os nós:

* load_source_file
* analyze_code
* generate_documentation
* export_markdown

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

Adicionar validações e decisões utilizando arestas condicionais (Conditional Edges), tornando o fluxo mais próximo de um agente real.

## Fluxo desejado

```text
                START
                  │
                  ▼
         load_source_file
                                                                        │
                                                                        ▼
                                (file validation router)
                                         │              │
                                         │ válido       │ inválido
                                         ▼              ▼
                         analyze_code    finish_with_error
          │
          ▼
     validate_analysis
          │              │
          │ sucesso      │ falha
          ▼              ▼
generate_documentation finish_with_error
          │
          ▼
 export_markdown
          │
          ▼
          END
```

## Requisitos

Criar os seguintes novos nós:

### validate_source_file

Responsável por verificar:

* arquivo existe
* extensão é `.cs`
* conteúdo não está vazio

Caso alguma validação falhe:

* preencher `errors` no estado
* direcionar para `finish_with_error`

Observação: nesta implementação a validação leve do arquivo foi feita como um "router"
ligado a `load_source_file` (função `should_continue_after_file_validation` em
`app/routers.py`) que também garante a leitura e população de `source_code` quando
necessário. Isso evita atualizações concorrentes no estado que ocorreriam ao usar um
nó separado que escreva os mesmos campos.

### validate_analysis

Após a análise do código, verificar se informações mínimas foram extraídas.

Por exemplo:

* nome da classe
* namespace (opcional)
* pelo menos um método

Caso não seja possível gerar documentação de qualidade:

* registrar erro
* interromper o fluxo

### finish_with_error

Último nó responsável por:

* registrar mensagem amigável
* retornar o estado sem lançar exceções

Implementação: o nó `finish_with_error` em `app/nodes.py` marca `success=False`
e preserva `errors` para apresentação ao usuário.

## Estado

Caso necessário, evoluir o AgentState adicionando campos úteis como:

* success
* errors
* warnings

Mantendo compatibilidade com o restante do projeto.

## Graph

Modificar `build_graph()` para utilizar:

* `add_conditional_edges()` para roteamento condicional
* funções de roteamento em `app/routers.py`:
        - `should_continue_after_file_validation` (validação e leitura leve do arquivo)
        - `should_continue_after_analysis`
* nós em `app/nodes.py` usados no fluxo:
        - `analyze_code_full` (análise com extração mínima de `class_name` e `methods`)
        - `validate_analysis`
        - `generate_documentation`
        - `export_markdown`
        - `finish_with_error`

Observação: `analyze_code` foi mantido como stub para compatibilidade com testes
unitários; o fluxo principal usa `analyze_code_full` para produzir dados mínimos
necessários à validação.

Evitar lógica complexa dentro do próprio grafo.

## Organização

As funções de decisão (routers) devem ficar separadas das implementações dos nós.

Exemplo:

* should_continue_after_file_validation()
* should_continue_after_analysis()

## Boas práticas

* código limpo
* type hints
* funções pequenas
* comentários apenas quando agregarem valor
* preparado para futuras expansões (ex.: memória, tools, human-in-the-loop)

O objetivo **não é aumentar a complexidade**, mas demonstrar o uso adequado dos recursos do LangGraph em um fluxo realista.
