
from src.chatbot import create_bot


def main():
    application = create_bot()

    print("Repozium Telegram Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
