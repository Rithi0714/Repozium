import os
import shutil
from pathlib import Path
from git import Repo


class RepositoryLoader:
    """
    Handles cloning a GitHub repository and loading
    supported source files into memory.
    """

    def __init__(self):

        # Temporary location where repositories are cloned
        self.workspace = Path("workspace")

        # File extensions we want to read
        self.supported_extensions = {
            ".py",
            ".java",
            ".js",
            ".ts",
            ".cpp",
            ".c",
            ".go",
            ".rs",
            ".md",
            ".txt",
        }

        # Directories we don't want to scan
        self.ignored_directories = {
            ".git",
            "node_modules",
            "venv",
            "__pycache__",
            "dist",
            "build",
            ".idea",
            ".vscode",
        }

        # Create workspace if it doesn't exist
        self.workspace.mkdir(exist_ok=True)

    def clone_repository(self, repo_url: str) -> Path:
        """
        Clone the repository into the workspace folder.
        Returns the path of the cloned repository.
        """

        repo_name = repo_url.rstrip("/").split("/")[-1]

        repo_path = self.workspace / repo_name

        # Remove existing copy
        if repo_path.exists():
            shutil.rmtree(repo_path)

        print(f"Cloning {repo_name}...")

        Repo.clone_from(repo_url, repo_path)

        print("Repository cloned successfully.\n")

        return repo_path

    def load_files(self, repo_path: Path) -> dict:
        """
        Reads all supported files and returns a dictionary.
        """

        repository_data = {}

        for root, dirs, files in os.walk(repo_path):

            # Skip unwanted directories
            dirs[:] = [
                d for d in dirs
                if d not in self.ignored_directories
            ]

            for file in files:

                file_path = Path(root) / file

                if file_path.suffix not in self.supported_extensions:
                    continue

                try:

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore",
                    ) as f:

                        repository_data[
                            str(file_path.relative_to(repo_path))
                        ] = f.read()

                except Exception as e:

                    print(f"Could not read {file_path}: {e}")

        return repository_data

    def cleanup(self, repo_path: Path):
        """
        Delete cloned repository after processing.
        """

        if repo_path.exists():
            shutil.rmtree(repo_path)