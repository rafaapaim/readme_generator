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

def read_instructions_from_code() -> list[dict]:
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
