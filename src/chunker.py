import ast
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter

class CodeChunker:

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200
        )


def detect_language(self, file_path: str):

    extension = Path(file_path).suffix.lower()

    mapping = {

        ".py": "python",

        ".java": "java",

        ".md": "markdown",

        ".txt": "text",

        ".js": "javascript",

        ".ts": "typescript"

    }

    return mapping.get(extension, "unknown")

def chunk_repository(self, repository_data):

    chunks = []

    for file_path, content in repository_data.items():

        language = self.detect_language(file_path)

        if language == "python":

            chunks.extend(
                self.chunk_python(
                    file_path,
                    content
                )
            )

        else:

            chunks.extend(
                self.chunk_text(
                    file_path,
                    content,
                    language
                )
            )

    return chunks


def chunk_python(
        self,
        file_path,
        content
):

    chunks = []

    try:
      tree = ast.parse(content)

    except SyntaxError:
       return []

    for node in tree.body:

        if isinstance(node, ast.ClassDef):

            chunks.extend(

                self.extract_class(
                    node,
                    content,
                    file_path
                )

            )

        elif isinstance(node, ast.FunctionDef):

            chunks.extend(

                self.create_metadata(

                    file_path=file_path,

                    language="python",

                    chunk_type="function",

                    class_name=None,

                    function_name=node.name,

                    start_line=node.lineno,

                    end_line=node.end_lineno,

                    content=ast.get_source_segment(
                        content,
                        node
                    )

                )

            )

    return chunks


def extract_class(
        self,
        class_node,
        content,
        file_path
):

    chunks = []

    for node in class_node.body:

        if isinstance(node, ast.FunctionDef):

            chunks.extend(

                self.create_metadata(

                    file_path=file_path,

                    language="python",

                    chunk_type="method",

                    class_name=class_node.name,

                    function_name=node.name,

                    start_line=node.lineno,

                    end_line=node.end_lineno,

                    content=ast.get_source_segment(
                        content,
                        node
                    )

                )

            )

    return chunks


def create_metadata(

        self,

        file_path,

        language,

        chunk_type,

        class_name,

        function_name,

        start_line,

        end_line,

        content

):

    if content is None:

        content = ""

    if len(content) > 1200:

        split_chunks = self.text_splitter.split_text(content)

    else:

        split_chunks = [content]

    final_chunks = []

    for index, chunk in enumerate(split_chunks):

        final_chunks.append({

            "file_path": file_path,

            "language": language,

            "chunk_type": chunk_type,

            "class_name": class_name,

            "function_name": function_name,

            "start_line": start_line,

            "end_line": end_line,

            "chunk_id": index,

            "content": chunk

        })

    return final_chunks

def chunk_text(
        self,
        file_path,
        content,
        language
):

    chunks = []

    split_text = self.text_splitter.split_text(content)

    for index, chunk in enumerate(split_text):

        chunks.append({

            "file_path": file_path,

            "language": language,

            "chunk_type": "text",

            "class_name": None,

            "function_name": None,

            "start_line": None,

            "end_line": None,

            "chunk_id": index,

            "content": chunk

        })

    return chunks