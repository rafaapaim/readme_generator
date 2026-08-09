from ast import Import, ImportFrom, AsyncFunctionDef, ClassDef, FunctionDef, iter_child_nodes, parse
from pathlib import Path

from google.adk import Agent


def generate_readme(instructions: list[dict]) -> str:
    """
    Gera um README.md atualizado com base nas instruções fornecidas.

    Args:
        instructions (list[dict]): Lista de instruções que descrevem as alterações no código.

    Returns:
        str: Conteúdo atualizado do README.md.
    """
    def normalize_instruction(item):
        if isinstance(item, dict):
            return (
                item.get("opname") or item.get("name") or item.get("op") or "instruction",
                item.get("argrepr") or item.get("argval") or item.get("arg") or "",
            )
        if isinstance(item, (list, tuple)):
            opname = item[0] if len(item) > 0 else "instruction"
            argrepr = item[4] if len(item) > 4 else str(item)
            return opname, argrepr
        return str(item), ""

    readme_content = "# README.md Atualizado\n\n"
    readme_content += "## Funcionalidades Implementadas\n"

    for instruction in instructions:
        opname, argrepr = normalize_instruction(instruction)
        readme_content += f"- {opname}: {argrepr}\n"

    readme_content += "\n## Instruções de Uso\n"
    readme_content += "1. Clone o repositório.\n"
    readme_content += "2. Instale as dependências.\n"
    readme_content += "3. Execute o projeto conforme as instruções específicas.\n"

    readme_content += "\n## Dependências\n"
    readme_content += "- Python 3.x\n"
    readme_content += "- Bibliotecas necessárias (ver requirements.txt)\n"

    readme_content += "\n## Contribuição\n"
    readme_content += "Sinta-se à vontade para contribuir com melhorias e correções.\n"

    return readme_content


def update_readme(instructions: list[dict]) -> None:
    """
    Atualiza o README.md com base nas instruções fornecidas.

    Args:
        instructions (list[dict]): Lista de instruções que descrevem as alterações no código.
    """
    readme_content = generate_readme(instructions)
    repo_root = Path(__file__).resolve().parent.parent
    readme_path = repo_root / "README.md"

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)

    print(f"README.md atualizado em {readme_path}")

def ler_instructions_from_code() -> list[dict]:
    """
    Lê as instruções do código-fonte para identificar alterações.

    Returns:
        list[dict]: Lista de instruções que descrevem as alterações no código.
    """
    repo_root = Path(__file__).resolve().parent.parent
    instructions: list[dict] = []

    def add_instruction(opname: str, argrepr: str, lineno: int) -> None:
        instructions.append(
            {
                "opname": opname,
                "argrepr": argrepr,
                "lineno": lineno,
                "path": str(path.relative_to(repo_root)),
            }
        )

    ignore_dirs = {".venv", ".git", "__pycache__"}

    for path in repo_root.rglob("*.py"):
        if any(part in ignore_dirs for part in path.parts):
            continue

        try:
            source = path.read_text(encoding="utf-8")
            tree = parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in iter_child_nodes(tree):
            if isinstance(node, Import):
                for alias in node.names:
                    name = alias.name
                    alias_text = f" as {alias.asname}" if alias.asname else ""
                    add_instruction("import", f"import {name}{alias_text}", node.lineno)
            elif isinstance(node, ImportFrom):
                module = node.module or ""
                names = ", ".join(
                    alias.name + (f" as {alias.asname}" if alias.asname else "")
                    for alias in node.names
                )
                add_instruction("from-import", f"from {module} import {names}", node.lineno)
            elif isinstance(node, FunctionDef):
                add_instruction("define-function", f"def {node.name}(...)", node.lineno)
            elif isinstance(node, AsyncFunctionDef):
                add_instruction("define-async-function", f"async def {node.name}(...)", node.lineno)
            elif isinstance(node, ClassDef):
                add_instruction("define-class", f"class {node.name}(...)", node.lineno)

    return instructions

def escrever_readme_atualizado():
    """
    Função principal para gerar e atualizar o README.md com base nas instruções do código.
    """
    instructions = ler_instructions_from_code()
    update_readme(instructions)


root_agent = Agent(
    name='areadme_generator',
    model='gemini-3.1-flash-lite',
    instruction="""
    Você é um especialista em Desenvolvimento de Software e Engenharia de Sistemas e é responsável por
    escrever/atualizar o README.md conforme forem feitas atualizações no código do projeto que está na pasta src em diante. 
    Não leve em consideração arquivos que não estejam na pasta src em diante.
    Então, você deve analisar o código e gerar um README.md atualizado e salvar na raiz do projeto, incluindo informações sobre as funcionalidades implementadas, 
    instruções de uso, dependências e quaisquer outras informações relevantes para os desenvolvedores que irão 
    utilizar ou contribuir para o projeto.
    """,
    tools=[generate_readme, update_readme, ler_instructions_from_code, escrever_readme_atualizado]
)
