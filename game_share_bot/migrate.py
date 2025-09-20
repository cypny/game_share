import subprocess


def run_command(command):
    """Выполняет команду и выводит весь вывод"""
    print(f"$ {command}")
    result = subprocess.run(command.split(), capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)


def run_migrations():
    run_command("alembic revision --autogenerate")
    run_command("alembic upgrade head")


if __name__ == "__main__":
    run_migrations()
