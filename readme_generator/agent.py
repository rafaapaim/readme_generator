import ast
from ast import Import, ImportFrom, AsyncFunctionDef, ClassDef, FunctionDef, iter_child_nodes, parse
from pathlib import Path
import tomllib

from google.adk import Agent


def get_pyproject_metadata() -> dict[str, str]:
    repo_root = Path(__file__).resolve().parent.parent
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return {}

    try:
        with open(pyproject_path, "rb") as f:
            project = tomllib.load(f).get("project", {})
        return {
            "name": str(project.get("name", "")),
            "description": str(project.get("description", "")),
        }
    except Exception:
        return {}


def get_project_name() -> str:
    metadata = get_pyproject_metadata()
    if metadata.get("name"):
        return metadata["name"]
    return Path(__file__).resolve().parent.parent.name


def get_project_description() -> str:
    metadata = get_pyproject_metadata()
    if metadata.get("description"):
        return metadata["description"]
    return "Aplicação simples em FastAPI gerada a partir do código em `src/`."


def get_python_requires() -> str:
    repo_root = Path(__file__).resolve().parent.parent
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return "Python 3.x"

    try:
        with open(pyproject_path, "rb") as f:
            project = tomllib.load(f).get("project", {})
        requires = project.get("requires-python") or project.get("python_requires")
        return str(requires) if requires else "Python 3.x"
    except Exception:
        return "Python 3.x"


def format_python_requires(requirement: str) -> str:
    if requirement.startswith(">="):
        return requirement.replace(">=", "Python ") + "+"
    if requirement.startswith("=="):
        return requirement.replace("==", "Python ")
    return requirement


def has_fastapi(imports: list[str]) -> bool:
    return any("fastapi" in item.lower() for item in imports)


def has_uvicorn(imports: list[str]) -> bool:
    return any("uvicorn" in item.lower() for item in imports)


def extract_imports(instructions: list[dict]) -> list[str]:
    imports = []
    for instruction in instructions:
        if isinstance(instruction, dict) and instruction.get("opname") in {"import", "from-import"}:
            imports.append(instruction.get("argrepr", ""))
    return imports


def extract_fastapi_routes() -> list[dict]:
    repo_root = Path(__file__).resolve().parent.parent
    src_root = repo_root / "src"
    routes: list[dict] = []
    if not src_root.exists():
        return routes

    for file_path in src_root.rglob("*.py"):
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                        if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == "app":
                            method = decorator.func.attr.upper()
                            route_path = None
                            if decorator.args:
                                first_arg = decorator.args[0]
                                if isinstance(first_arg, ast.Constant):
                                    route_path = first_arg.value
                                elif isinstance(first_arg, ast.Str):
                                    route_path = first_arg.s
                            routes.append({
                                "method": method,
                                "path": route_path or "<path não detectado>",
                                "function": node.name,
                                "file": str(file_path.relative_to(repo_root)),
                            })
    return routes


def list_src_files() -> list[str]:
    repo_root = Path(__file__).resolve().parent.parent
    src_root = repo_root / "src"
    if not src_root.exists():
        return []
    return [str(path.relative_to(repo_root)) for path in sorted(src_root.rglob("*.py"))]


def generate_readme(instructions: list[dict]) -> str:
    """
    Gera um README.md atualizado com base nas instruções fornecidas.

    Args:
        instructions (list[dict]): Lista de instruções que descrevem as alterações no código.

    Returns:
        str: Conteúdo atualizado do README.md.
    """
    imports = extract_imports(instructions)
    functions = [item for item in instructions if isinstance(item, dict) and item.get("opname") == "define-function"]
    routes = extract_fastapi_routes()
    src_files = list_src_files()
    project_name = get_project_name()
    python_requires_raw = get_python_requires()
    python_requires = format_python_requires(python_requires_raw)
    project_description = get_project_description()

    uses_fastapi = bool(routes or has_fastapi(imports))
    uses_uvicorn = has_uvicorn(imports)

    readme_content = f"# {project_name}\n\n"
    readme_content += f"{project_description}\n\n"

    readme_content += "## Visão geral\n"
    if uses_fastapi and routes:
        readme_content += f"Aplicação FastAPI com {len(routes)} endpoint(s) identificados em `src/`.\n\n"
    elif uses_fastapi:
        readme_content += "Aplicação FastAPI com endpoints definidos no código em `src/`.\n\n"
    elif functions:
        readme_content += f"Projeto Python com {len(functions)} função(ões) detectada(s) em `src/`.\n\n"
    else:
        readme_content += "Projeto Python com código em `src/`.\n\n"

    if routes:
        readme_content += "## Endpoints detectados\n"
        for route in routes:
            readme_content += f"- `{route['method']} {route['path']}` em `{route['file']}` (função `{route['function']}`)\n"
        readme_content += "\n"

    if functions:
        readme_content += "## Funções detectadas\n"
        for function in functions:
            readme_content += f"- {function.get('argrepr')}\n"
        readme_content += "\n"

    if imports:
        readme_content += "## Imports detectados\n"
        for item in imports:
            readme_content += f"- `{item}`\n"
        readme_content += "\n"

    readme_content += "## Tecnologias e dependências\n"
    readme_content += f"- {python_requires}\n"
    if uses_fastapi:
        readme_content += "- FastAPI\n"
    if uses_uvicorn:
        readme_content += "- Uvicorn\n"
    if not uses_fastapi and not uses_uvicorn:
        readme_content += "- Dependências identificadas a partir do código\n"
    readme_content += "- google-adk (para o agente de geração de README)\n\n"

    readme_content += "## Estrutura do projeto\n"
    if src_files:
        for file_path in src_files:
            readme_content += f"- `{file_path}`\n"
    else:
        readme_content += "- Nenhum arquivo `src/*.py` encontrado\n"
    readme_content += "- `readme_generator/agent.py`\n"
    readme_content += "- `README.md`\n\n"

    readme_content += "## Pré-requisitos\n"
    readme_content += f"- {python_requires} instalado\n"
    readme_content += "- Ambiente virtual recomendado\n\n"

    readme_content += "## Instalação\n"
    readme_content += "```bash\n"
    readme_content += "python -m venv .venv\n"
    readme_content += "source .venv/bin/activate  # Linux/macOS\n"
    readme_content += ".venv\\Scripts\\activate  # Windows\n"
    if (Path(__file__).resolve().parent.parent / 'src' / 'requirements.txt').exists():
        readme_content += "pip install -r src/requirements.txt\n"
    elif (Path(__file__).resolve().parent.parent / 'requirements.txt').exists():
        readme_content += "pip install -r requirements.txt\n"
    else:
        readme_content += "pip install -r requirements.txt  # ajuste conforme seu projeto\n"
    readme_content += "```\n\n"

    if uses_fastapi:
        readme_content += "## Execução\n"
        readme_content += "```bash\n"
        readme_content += "uvicorn src.main:app --reload --host 0.0.0.0 --port 8000\n"
        readme_content += "```\n\n"

    readme_content += "## Uso\n"
    if routes:
        readme_content += "Use os endpoints listados acima para testar a API localmente.\n"
        readme_content += "Por exemplo, acesse `http://localhost:8000/` no navegador ou via curl.\n\n"
    else:
        readme_content += "Execute a aplicação conforme as instruções acima e verifique a saída esperada.\n\n"

    readme_content += "## Dependências atuais\n"
    dependencies = get_project_dependencies()
    if dependencies:
        for package in sorted(dependencies):
            readme_content += f"- {package}\n"
    else:
        readme_content += "- Dependências não identificadas automaticamente\n"
    readme_content += "\n"

    readme_content += "## Contribuição\n"
    readme_content += "Contribuições são bem-vindas. Abra issues ou pull requests para melhorias.\n"

    return readme_content


def get_project_dependencies() -> list[str]:
    repo_root = Path(__file__).resolve().parent.parent
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return ["Python 3.x", "FastAPI", "Uvicorn"]

    try:
        with open(pyproject_path, "rb") as f:
            project = tomllib.load(f)
        deps = project.get("project", {}).get("dependencies", [])
        return [str(dep) for dep in deps]
    except Exception:
        return ["Python 3.x", "FastAPI", "Uvicorn"]


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

def read_instructions_from_code() -> list[dict]:
    """
    Lê as instruções do código-fonte para identificar alterações.

    Returns:
        list[dict]: Lista de instruções que descrevem as alterações no código.
    """
    repo_root = Path(__file__).resolve().parent.parent
    src_root = repo_root / "src"
    instructions: list[dict] = []

    def add_instruction(opname: str, argrepr: str, lineno: int, path: Path) -> None:
        instructions.append(
            {
                "opname": opname,
                "argrepr": argrepr,
                "lineno": lineno,
                "path": str(path.relative_to(repo_root)),
            }
        )

    ignore_dirs = {".venv", ".git", "__pycache__"}

    if not src_root.exists():
        return instructions

    for path in src_root.rglob("*.py"):
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
                    add_instruction("import", f"import {name}{alias_text}", node.lineno, path)
            elif isinstance(node, ImportFrom):
                module = node.module or ""
                names = ", ".join(
                    alias.name + (f" as {alias.asname}" if alias.asname else "")
                    for alias in node.names
                )
                add_instruction("from-import", f"from {module} import {names}", node.lineno, path)
            elif isinstance(node, FunctionDef):
                add_instruction("define-function", f"def {node.name}(...)", node.lineno, path)
            elif isinstance(node, AsyncFunctionDef):
                add_instruction("define-async-function", f"async def {node.name}(...)", node.lineno, path)
            elif isinstance(node, ClassDef):
                add_instruction("define-class", f"class {node.name}(...)", node.lineno, path)

    return instructions

def write_updated_readme():
    """
    Função principal para gerar e atualizar o README.md com base nas instruções do código.
    """
    instructions = read_instructions_from_code()
    update_readme(instructions)


root_agent = Agent(
    name='readme_generator',
    model='gemini-3.1-flash-lite',
    instruction = """
        Você é um especialista em Desenvolvimento de Software, Engenharia de Software e Documentação Técnica.

        Sua responsabilidade é analisar o código-fonte do projeto e criar ou atualizar o arquivo README.md localizado na raiz do projeto.

        ## Escopo de análise

        - Considere exclusivamente os arquivos e diretórios localizados dentro da pasta `src`.
        - Não utilize como fonte de informação arquivos fora de `src`.
        - Analise o código-fonte existente para identificar funcionalidades, arquitetura, componentes, dependências, fluxos e comportamentos implementados.
        - Não faça alterações no código-fonte do projeto.
        - O README.md deve refletir o estado atual do código analisado.

        ## Regras para criação ou atualização

        Ao executar, determine se já existe um `README.md` na raiz do projeto:

        - Se não existir, crie um novo README.md.
        - Se existir, atualize seu conteúdo com base no código atual.
        - Preserve informações relevantes que já estejam documentadas e que continuem válidas.
        - Remova ou corrija informações que estejam desatualizadas ou incompatíveis com o código atual.
        - Não duplique informações desnecessariamente.
        - Não invente funcionalidades, comandos, dependências, configurações ou comportamentos que não possam ser identificados no código analisado.
        - Quando uma informação não puder ser determinada com segurança a partir do código, não faça suposições.

        ## Conteúdo do README.md

        Sempre que houver informações suficientes no código, o README.md deve conter:

        1. Nome e descrição do projeto
        2. Objetivo do projeto
        3. Principais funcionalidades implementadas
        4. Tecnologias e dependências utilizadas
        5. Estrutura relevante do projeto
        6. Pré-requisitos para execução
        7. Instruções para instalação e configuração
        8. Instruções para execução
        9. Exemplos de uso, quando aplicável
        10. Informações sobre configuração e variáveis de ambiente, quando identificáveis
        11. Informações relevantes para desenvolvedores que desejam contribuir ou modificar o projeto

        Não é obrigatório incluir uma seção quando não houver informações suficientes para preenchê-la corretamente.

        ## Qualidade da documentação

        - Escreva o README em Markdown válido e bem estruturado.
        - Utilize títulos, subtítulos, listas, tabelas e blocos de código quando contribuírem para a clareza.
        - Seja objetivo e evite explicações desnecessariamente longas.
        - Utilize terminologia técnica adequada.
        - Os comandos apresentados devem ser compatíveis com o projeto analisado.
        - Os exemplos devem refletir funcionalidades realmente existentes.
        - Priorize informações úteis para um desenvolvedor que acabou de clonar o projeto e precisa entender, instalar, executar e utilizar a aplicação.

        ## Resultado

        Ao finalizar a análise:

        1. Gere ou atualize o arquivo `README.md`.
        2. Salve o arquivo na raiz do projeto.
        3. Garanta que o conteúdo esteja consistente com o código existente em `src`.
        4. Não altere nenhum outro arquivo do projeto.
        """,
    tools=[generate_readme, update_readme, read_instructions_from_code, write_updated_readme]
)
