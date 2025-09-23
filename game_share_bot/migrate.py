import subprocess
from pathlib import Path

def run_command(command):
    """Выполняет команду и выводит весь вывод"""
    print(f"$ {command}")
    result = subprocess.run(command.split(), capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)


def create_logs_directory():
    """Создает папку для логов"""
    logs_path = Path("logs")
    logs_path.mkdir(exist_ok=True)


def run_migrations():
    create_logs_directory()
    run_command("alembic revision --autogenerate")
    run_command("alembic upgrade head")


if __name__ == "__main__":
    run_migrations()
