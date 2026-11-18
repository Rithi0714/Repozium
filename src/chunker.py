
import ast
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


class CodeChunker:

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            separators=[
                "\n\n",
                "\n",
                " ",
                ""
            ]
        )

    def detect_language(self, file_path: str):

        extension = Path(file_path).suffix.lower()

        mapping = {
            ".py": "python",
            ".java": "java",
            ".md": "markdown",
            ".txt": "text",
            ".js": "javascript",
            ".ts": "typescript",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust"
        }

        return mapping.get(extension, "unknown")

    def chunk_repository(self, repository_data):

        chunks = []

        for file_path, content in repository_data.items():

            if not content or not content.strip():
                continue

            language = self.detect_language(file_path)

            if language == "python":

                file_chunks = self.chunk_python(
                    file_path,
                    content
                )

            else:

                file_chunks = self.chunk_text(
                    file_path,
                    content,
                    language
                )

            chunks.extend(file_chunks)

        return chunks

    def chunk_python(self, file_path, content):

        chunks = []

        try:
            tree = ast.parse(content)

        except SyntaxError:
            return self.chunk_text(
                file_path,
                content,
                "python"
            )

        # Extract module-level classes and functions.
        for node in tree.body:

            if isinstance(node, ast.ClassDef):

                class_chunks = self.extract_class(
                    node,
                    content,
                    file_path
                )

                chunks.extend(class_chunks)

            elif isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):

                chunks.extend(
                    self.create_metadata(
                        file_path=file_path,
                        language="python",
                        chunk_type="function",
                        class_name=None,
                        function_name=node.name,
                        start_line=self.get_start_line(node),
                        end_line=node.end_lineno,
                        content=ast.get_source_segment(
                            content,
                            node
                        )
                    )
                )

        # Preserve files containing imports, constants,
        # or other statements that were not extracted.
        if not chunks:

            return self.chunk_text(
                file_path,
                content,
                "python"
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

            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):

                chunks.extend(
                    self.create_metadata(
                        file_path=file_path,
                        language="python",
                        chunk_type="method",
                        class_name=class_node.name,
                        function_name=node.name,
                        start_line=self.get_start_line(node),
                        end_line=node.end_lineno,
                        content=ast.get_source_segment(
                            content,
                            node
                        )
                    )
                )

        # Preserve classes without methods.
        if not chunks:

            class_content = ast.get_source_segment(
                content,
                class_node
            )

            chunks.extend(
                self.create_metadata(
                    file_path=file_path,
                    language="python",
                    chunk_type="class",
                    class_name=class_node.name,
                    function_name=None,
                    start_line=self.get_start_line(class_node),
                    end_line=class_node.end_lineno,
                    content=class_content
                )
            )

        return chunks

    def get_start_line(self, node):

        # Include decorators in the extracted source range.
        if getattr(node, "decorator_list", None):
            return min(
                decorator.lineno
                for decorator in node.decorator_list
            )

        return node.lineno

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

        if not content:
            return []

        if len(content) > 1200:

            split_chunks = self.text_splitter.split_text(
                content
            )

        else:

            split_chunks = [content]

        final_chunks = []

        for index, chunk in enumerate(split_chunks):

            final_chunks.append(
                {
                    "file_path": file_path,
                    "language": language,
                    "chunk_type": chunk_type,
                    "class_name": class_name,
                    "function_name": function_name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "chunk_id": index,
                    "content": chunk
                }
            )

        return final_chunks

    def chunk_text(
        self,
        file_path,
        content,
        language
    ):

        if not content or not content.strip():
            return []

        split_text = self.text_splitter.split_text(
            content
        )

        final_chunks = []

        current_position = 0

        for index, chunk in enumerate(split_text):

            # Estimate line ranges for text-based chunks.
            start_position = content.find(
                chunk,
                current_position
            )

            if start_position == -1:
                start_position = current_position

            end_position = start_position + len(chunk)

            start_line = (
                content.count("\n", 0, start_position) + 1
            )

            end_line = (
                content.count("\n", 0, end_position) + 1
            )

            final_chunks.append(
                {
                    "file_path": file_path,
                    "language": language,
                    "chunk_type": "text",
                    "class_name": None,
                    "function_name": None,
                    "start_line": start_line,
                    "end_line": end_line,
                    "chunk_id": index,
                    "content": chunk
                }
            )

            current_position = max(
                current_position,
                end_position - 200
            )

        return final_chunks
