# Objetivo

Implementar a integração do nó `generate_documentation` com um Large Language Model utilizando LangChain.

O restante da arquitetura do projeto deve permanecer inalterado.

## Objetivo do nó

O nó `generate_documentation` deve gerar documentação técnica em Markdown a partir das informações disponíveis no estado do agente.

Não deve realizar leitura de arquivos nem análise de código.

Sua única responsabilidade é transformar o estado atual em uma documentação técnica utilizando o LLM.

## Modelo

Criar a integração utilizando LangChain.

A instanciação do modelo deve ficar isolada em `config.py` por meio de uma função semelhante a:

```python
def get_llm():
    ...
```

O restante da aplicação nunca deve conhecer diretamente qual modelo está sendo utilizado.

## Prompt

Criar um prompt estruturado em `prompts.py`.

O prompt deve instruir o modelo a agir como um arquiteto de software experiente.

A documentação gerada deve conter, sempre que possível:

- nome da classe
- objetivo
- responsabilidades
- dependências
- métodos públicos
- parâmetros
- retornos
- possíveis exceções
- observações
- sugestões de melhoria, quando apropriado

A resposta deve ser obrigatoriamente em Markdown.

## Entrada do LLM

Utilizar tanto:

- informações estruturadas produzidas em `analyze_code`
- código-fonte original

Caso alguma informação estruturada ainda não exista, utilizar o que estiver disponível sem gerar erro.

## Implementação

No node `generate_documentation`:

- montar o prompt
- chamar o LLM
- armazenar o Markdown em `state["documentation"]`

Em caso de erro:

- registrar em `state["errors"]`
- não lançar exceções não tratadas

## Boas práticas

- utilizar LangChain
- utilizar mensagens System e Human
- separar construção do prompt da chamada ao modelo
- utilizar type hints
- manter o código organizado
- evitar lógica de negócio dentro do prompt

## Importante

A implementação deve ficar preparada para que futuramente seja possível trocar o provedor do modelo, como OpenAI, Groq, Gemini ou Ollama, alterando apenas `config.py`.
