# Objetivo

Adicionar suporte a memória utilizando **InMemorySaver** do LangGraph.

O objetivo desta implementação é preparar o agente para manter o estado entre múltiplas execuções de uma mesma sessão, utilizando o mecanismo oficial de checkpoint do LangGraph.

O restante da arquitetura deve permanecer inalterado.

## Implementação

Utilizar o checkpointer oficial:

```python
InMemorySaver
```

A memória deve ser integrada ao grafo, e não aos nodes.

## graph.py

Modificar `build_graph()` para que o grafo seja compilado utilizando um `checkpointer`.

A criação da memória deve ocorrer dentro do próprio `graph.py`.

Exemplo esperado (não necessariamente igual):

```python
memory = InMemorySaver()

graph = workflow.compile(
    checkpointer=memory
)
```

Não alterar o fluxo existente do agente.

## main.py

Atualizar a execução do grafo para utilizar um `thread_id`.

Utilizar o mecanismo recomendado pelo LangGraph:

```python
config = {
    "configurable": {
        "thread_id": "demo-session"
    }
}
```

Toda execução do grafo deve utilizar esse objeto de configuração.

## Objetivo da memória

A memória deverá permitir que múltiplas execuções utilizando o mesmo `thread_id` compartilhem o histórico do estado.

Neste momento não é necessário alterar a lógica dos nodes para utilizar esse histórico.

O objetivo é apenas deixar a infraestrutura preparada.

## Organização

A implementação deve manter a separação de responsabilidades:

* graph.py → construção do workflow e configuração da memória
* nodes.py → regras de negócio
* main.py → execução do agente
* state.py → definição do estado

Nenhum node deve criar ou manipular diretamente o checkpointer.

## Comentários

Adicionar comentários curtos explicando:

* o papel do `InMemorySaver`
* o motivo do uso do `thread_id`

## Boas práticas

* utilizar type hints
* manter compatibilidade com a implementação atual
* evitar duplicação de código
* não adicionar dependências desnecessárias
* seguir a documentação oficial do LangGraph

## Importante

Não alterar o comportamento atual do agente.

Após esta implementação, o projeto deve continuar executando exatamente o mesmo fluxo existente, porém preparado para reutilizar o estado entre execuções de uma mesma sessão através do `thread_id`.
