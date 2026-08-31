# Objetivo

Adicionar suporte a memória utilizando o mecanismo oficial de checkpoint do LangGraph.

O objetivo desta implementação é preparar o agente para manter o estado entre múltiplas execuções de uma mesma sessão.

O restante da arquitetura deve permanecer inalterado.

## Implementação

Utilizar um checkpointer oficial do LangGraph. A ideia inicial era usar:

```python
InMemorySaver
```

Na evolução do projeto, a implementação adotou `SqliteSaver` para persistência em disco, preservando o mesmo conceito de checkpoints e permitindo retomar execuções por `thread_id` mesmo após reiniciar o processo.

## graph.py

Modificar `build_graph()` para que o grafo seja compilado utilizando um `checkpointer`.

A criação da memória deve ocorrer dentro do próprio `graph.py`.

Exemplo conceitual:

```python
graph = workflow.compile(
    checkpointer=sqlite_saver
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

A memória deve permitir que múltiplas execuções com o mesmo `thread_id` compartilhem o histórico do estado.

Neste momento, não é necessário alterar a lógica dos nodes para utilizar esse histórico.

O objetivo é deixar a infraestrutura preparada.

## Organização

A implementação deve manter a separação de responsabilidades:

- `graph.py`: construção do workflow e configuração da memória
- `nodes.py`: regras de negócio
- `main.py`: execução do agente
- `state.py`: definição do estado

Nenhum node deve criar ou manipular diretamente o checkpointer.

## Boas práticas

- utilizar type hints
- manter compatibilidade com a implementação atual
- evitar duplicação de código
- não adicionar dependências desnecessárias
- seguir a documentação oficial do LangGraph

## Importante

Após esta implementação, o projeto deve continuar executando o mesmo fluxo existente, porém preparado para reutilizar o estado entre execuções de uma mesma sessão por meio do `thread_id`.
