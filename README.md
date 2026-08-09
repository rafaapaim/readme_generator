# estudo-agentes-ia

Projeto simples em FastAPI que expõe um endpoint `/` retornando uma mensagem JSON.

## Objetivo
Fornecer uma API mínima em FastAPI para servir um endpoint de saudação.

## Principais funcionalidades
- Endpoint HTTP GET em `/`
- Retorna um JSON com a chave `message`
- Funções analisadas no código:
  - def main(...)

## Tecnologias e dependências
- Python 3.13+
- FastAPI
- Uvicorn
- google-adk (para o agente de geração de README)

## Estrutura do projeto
- `src/main.py`: aplicação FastAPI
- `readme_generator/agent.py`: agente que lê o código e gera o README
- `README.md`: documentação principal do projeto

## Pré-requisitos
- Python 3.13 ou superior instalado
- ambiente virtual configurado

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows
pip install -r src/requirements.txt
```

## Execução
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Uso
Acesse `http://localhost:8000/` no navegador ou via curl para ver a resposta JSON.

## Dependências atuais
- google-adk===2.2.0

## Contribuição
Contribuições são bem-vindas. Abra issues ou pull requests para melhorias.
