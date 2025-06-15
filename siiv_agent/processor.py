import subprocess
from typing import Tuple


def run_black(file_path: str) -> Tuple[int, str, str]:
    print("running black")
    result = subprocess.run(["black", file_path], capture_output=True, text=True)
    return (result.returncode, result.stdout, result.stderr)


def run_isort(file_path: str) -> Tuple[int, str, str]:
    print("running isort")
    result = subprocess.run(["isort", file_path], capture_output=True, text=True)
    return (result.returncode, result.stdout, result.stderr)


def run_mypy(file_path: str) -> Tuple[int, str, str]:
    print("running mypy")
    result = subprocess.run(["mypy", file_path], capture_output=True, text=True)
    return (result.returncode, result.stdout, result.stderr)


def run_ruff(file_path: str) -> Tuple[int, str, str]:
    print("running ruff")
    result = subprocess.run(
        ["ruff", "check", file_path], capture_output=True, text=True
    )
    return (result.returncode, result.stdout, result.stderr)


def run_pytest(file_path: str) -> Tuple[int, str, str]:
    print("running pytest")
    result = subprocess.run(["pytest", file_path], capture_output=True, text=True)
    return (result.returncode, result.stdout, result.stderr)


def run_all(file_path: str) -> None:
    res = run_black(file_path=file_path)
    print(res)

    res = run_isort(file_path=file_path)
    print(res)

    res = run_mypy(file_path=file_path)
    print(res)

    res = run_ruff(file_path=file_path)
    print(res)

    res = run_pytest(file_path=file_path)
    print(res)


if __name__ == "__main__":
    import sys

    file_path = sys.argv[1]
    run_all(file_path=file_path)

# end
