# estudo-agentes-ia

Add your description here

## Visão geral
Aplicação FastAPI com 1 endpoint(s) identificados em `src/`.

## Endpoints detectados
- `GET /` em `src/main.py` (função `main`)

## Funções detectadas
- def main(...)

## Imports detectados
- `from fastapi import FastAPI`
- `import uvicorn`

## Tecnologias e dependências
- Python 3.13+
- FastAPI
- Uvicorn
- google-adk (para o agente de geração de README)

## Estrutura do projeto
- `src/main.py`
- `readme_generator/agent.py`
- `README.md`

## Pré-requisitos
- Python 3.13+ instalado
- Ambiente virtual recomendado

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
Use os endpoints listados acima para testar a API localmente.
Por exemplo, acesse `http://localhost:8000/` no navegador ou via curl.

## Dependências atuais
- google-adk===2.2.0

## Contribuição
Contribuições são bem-vindas. Abra issues ou pull requests para melhorias.
