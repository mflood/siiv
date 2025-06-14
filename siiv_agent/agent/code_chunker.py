import ast
from pathlib import Path
from dataclasses import dataclass
from typing import Generator, Optional, List, Union, Dict

@dataclass
class CodeChunk:
    code: str
    file_path: str
    start_line: int
    end_line: int
    symbol_name: Optional[str]
    code_type: str  # e.g. "function", "class", "import", "top_level"
    docstring: Optional[str]

    def to_metadata_dict(self) -> Dict[str, Optional[str]]:
        return_dict = {
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "symbol_name": self.symbol_name or "",
            "code_type": self.code_type,
            "docstring": self.docstring,
        }
        for key in return_dict:
            if return_dict[key] is None:
                return_dict[key] = ""
        return return_dict

def get_source_segment(source: str, node: ast.AST) -> str:
    """Return exact code for an AST node from source."""
    lines = source.splitlines(keepends=True)
    start = node.lineno - 1
    end = getattr(node, "end_lineno", node.lineno)  # Python >=3.8
    return "".join(lines[start:end])

def extract_code_chunks(file_path: Union[str, Path]) -> Generator[CodeChunk, None, None]:
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return
    # Track top-level code ranges for fallback chunk
    used_lines = set()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield CodeChunk(
                code=get_source_segment(source, node),
                file_path=str(path),
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                symbol_name=node.name,
                code_type="function",
                docstring=ast.get_docstring(node),
            )
            used_lines.update(range(node.lineno, getattr(node, "end_lineno", node.lineno)+1))

        elif isinstance(node, ast.ClassDef):
            yield CodeChunk(
                code=get_source_segment(source, node),
                file_path=str(path),
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                symbol_name=node.name,
                code_type="class",
                docstring=ast.get_docstring(node),
            )
            used_lines.update(range(node.lineno, getattr(node, "end_lineno", node.lineno)+1))

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            yield CodeChunk(
                code=get_source_segment(source, node),
                file_path=str(path),
                start_line=node.lineno,
                end_line=node.lineno,
                symbol_name=None,
                code_type="import",
                docstring=None,
            )
            used_lines.add(node.lineno)

    # Add top-level code chunk if any remaining lines
    top_level_lines = [
        (i, line) for i, line in enumerate(lines, start=1) if i not in used_lines and line.strip()
    ]
    if top_level_lines:
        start_line = top_level_lines[0][0]
        end_line = top_level_lines[-1][0]
        code = "\n".join(line for _, line in top_level_lines)
        yield CodeChunk(
            code=code,
            file_path=str(path),
            start_line=start_line,
            end_line=end_line,
            symbol_name=None,
            code_type="top_level",
            docstring=None,
        )
