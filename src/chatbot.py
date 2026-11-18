
import asyncio
import hashlib
import time
from urllib.parse import urlparse

import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from ingest import ingest_repository
from query import answer_question

load_dotenv()


def get_collection_name(user_id: int, repo_url: str) -> str:
    """Create a separate ChromaDB collection for each user and repository."""

    unique_key = f"{user_id}:{repo_url}"

    repo_hash = hashlib.sha256(
        unique_key.encode("utf-8")
    ).hexdigest()[:16]

    return f"repo_{repo_hash}"


def is_github_url(text: str) -> bool:
    """Check whether the message contains a GitHub repository URL."""

    try:
        parsed = urlparse(text.strip())

        if parsed.scheme not in ("https", "http"):
            return False

        if parsed.netloc.lower() not in (
            "github.com",
            "www.github.com"
        ):
            return False

        parts = [
            part for part in parsed.path.strip("/").split("/")
            if part
        ]

        return len(parts) == 2

    except Exception:
        return False


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Hello! Welcome to Repozium AI Assistant.\n\n"
        "I help you understand GitHub repositories using AI.\n\n"
        "To get started, send me a public GitHub repository URL.\n\n"
        "Example:\n"
        "https://github.com/username/repository\n\n"
        "After indexing, you can ask questions about its code."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "REPOZIUM - HELP\n\n"
        "1. Send a public GitHub repository URL.\n"
        "2. Wait for indexing to finish.\n"
        "3. Ask questions about its code.\n\n"
        "Commands:\n"
        "/start - Start Repozium\n"
        "/help - Show instructions\n"
        "/repo - Connect another repository\n"
        "/status - Show current repository\n"
        "/clear - Disconnect current repository"
    )


async def repo_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Please send the public GitHub repository URL "
        "you want to connect.\n\n"
        "Example:\n"
        "https://github.com/username/repository"
    )


async def status_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    repo_url = context.user_data.get("repo_url")

    if not repo_url:
        await update.message.reply_text(
            "No repository is currently connected.\n"
            "Send a GitHub repository URL to get started."
        )
        return

    await update.message.reply_text(
        f"Connected repository:\n{repo_url}\n\n"
        "You can ask questions about its code."
    )


async def clear_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data.pop("repo_url", None)
    context.user_data.pop("collection_name", None)

    await update.message.reply_text(
        "Your active repository connection has been cleared.\n\n"
        "Send another GitHub repository URL to get started."
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.message.text.strip()

    # STEP 1: Check whether the user sent a GitHub URL.
    if is_github_url(message):

        repo_url = message.rstrip("/")

        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        collection_name = get_collection_name(
            update.effective_user.id,
            repo_url
        )

        status_message = await update.message.reply_text(
            "Repository received!\n\n"
            "Cloning and indexing your repository. "
            "This may take a few minutes..."
        )

        try:
            result = await asyncio.to_thread(
                ingest_repository,
                repo_url,
                collection_name
            )

            context.user_data["repo_url"] = repo_url
            context.user_data["collection_name"] = collection_name

            await status_message.edit_text(
                "Repository indexed successfully!\n\n"
                f"Repository: {repo_url}\n"
                f"Files processed: {result['files']}\n"
                f"Chunks created: {result['chunks']}\n"
                f"Chunks stored: {result['total_stored']}\n\n"
                "You can now ask questions about your code."
            )

        except Exception as error:
            await status_message.edit_text(
                "Sorry, I couldn't index this repository.\n\n"
                f"Error: {str(error)[:1000]}\n\n"
                "Please check the repository URL and try again."
            )

        return

    # STEP 2: Check whether a repository is connected.
    collection_name = context.user_data.get("collection_name")

    if not collection_name:
        await update.message.reply_text(
            "Please connect a GitHub repository first.\n\n"
            "Send a GitHub repository URL to get started."
        )
        return

    # STEP 3: Process the user's question.
    status_message = await update.message.reply_text(
        "Searching your repository and preparing an answer..."
    )

    try:
        start_time = time.time()

        answer = await asyncio.to_thread(
            answer_question,
            message,
            collection_name
        )

        elapsed_time = time.time() - start_time

        print(
            f"Question processing time: "
            f"{elapsed_time:.2f} seconds"
        )

        await status_message.edit_text(
            answer[:4000]
        )

    except Exception as error:
        await status_message.edit_text(
            "Sorry, I couldn't process your question.\n\n"
            f"Error: {str(error)[:1000]}"
        )


def create_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not found in .env"
        )

    application = (
        Application.builder()
        .token(token)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("repo", repo_command)
    )

    application.add_handler(
        CommandHandler("status", status_command)
    )

    application.add_handler(
        CommandHandler("clear", clear_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    return application
