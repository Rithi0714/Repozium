
import os
import shutil
import stat
import hashlib
from pathlib import Path

from git import Repo


class RepositoryLoader:
    """
    Handles cloning GitHub repositories and loading
    supported source files safely.
    """

    def __init__(self):

        self.workspace = Path("workspace")

        self.max_file_size = 1 * 1024 * 1024  # 1 MB

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

        self.ignored_directories = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".idea",
            ".vscode",
            ".next",
            "coverage",
            "target",
            "vendor",
            ".gradle",
        }

        self.ignored_files = {
            ".env",
            ".env.local",
            ".env.production",
            "id_rsa",
            "id_ed25519",
            "credentials",
            "secrets.txt",
        }

        self.workspace.mkdir(
            parents=True,
            exist_ok=True
        )

    def clone_repository(self, repo_url: str) -> Path:
        """
        Clone a repository into a unique workspace directory.
        """

        repo_name = repo_url.rstrip("/").split("/")[-1]

        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        repo_hash = hashlib.sha256(
            repo_url.encode("utf-8")
        ).hexdigest()[:10]

        repo_path = self.workspace / f"{repo_name}_{repo_hash}"

        if repo_path.exists():

            print("Removing existing repository copy...")

            self._remove_directory(repo_path)

        print(f"Cloning {repo_name}...")

        Repo.clone_from(
            repo_url,
            repo_path
        )

        print("Repository cloned successfully.\n")

        return repo_path

    def load_files(self, repo_path: Path) -> dict:
        """
        Read supported source files into memory.
        """

        repository_data = {}

        for root, dirs, files in os.walk(repo_path):

            dirs[:] = [
                directory
                for directory in dirs
                if directory not in self.ignored_directories
            ]

            for file in files:

                file_path = Path(root) / file

                if file.lower() in self.ignored_files:
                    continue

                if file_path.suffix.lower() not in self.supported_extensions:
                    continue

                try:

                    # Avoid loading extremely large files.
                    if file_path.stat().st_size > self.max_file_size:
                        print(f"Skipping large file: {file_path}")
                        continue

                    relative_path = file_path.relative_to(
                        repo_path
                    )

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:

                        content = f.read()

                    if content.strip():

                        repository_data[
                            str(relative_path)
                        ] = content

                except Exception as error:

                    print(
                        f"Could not read {file_path}: {error}"
                    )

        return repository_data

    def cleanup(self, repo_path: Path):
        """
        Remove temporary repository after ingestion.
        """

        if repo_path.exists():

            print("Removing temporary repository...")

            self._remove_directory(repo_path)

            print("Temporary repository removed.")
            print("Cleanup completed.")

    def _remove_directory(self, directory: Path):
        """
        Safely remove directories, including read-only files.
        """

        def handle_remove_error(
            function,
            path,
            exc_info
        ):

            os.chmod(
                path,
                stat.S_IWRITE
            )

            function(path)

        shutil.rmtree(
            directory,
            onerror=handle_remove_error
        )
