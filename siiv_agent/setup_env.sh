#!/bin/bash

set -e  # exit immediately on error
set -o pipefail

VENV_NAME="siiv_agent"
PYTHON_VERSION="3.13.3"

echo "▶ Starting virtual environment setup for '$VENV_NAME'..."

# 1️⃣ Try to locate python3.13 first
PYTHON_BIN=$(command -v python3.13 || true)

# 2️⃣ Try to locate python via pyenv if not found
if [[ -z "$PYTHON_BIN" ]]; then
    if command -v pyenv >/dev/null 2>&1; then
        echo "🔎 python3.13 not found directly. Trying pyenv..."
        if pyenv versions --bare | grep -q "$PYTHON_VERSION"; then
            pyenv shell "$PYTHON_VERSION"
            PYTHON_BIN=$(pyenv which python)
        else
            echo "❌ Python $PYTHON_VERSION not installed in pyenv."
            echo "You can install it with: pyenv install $PYTHON_VERSION"
            exit 1
        fi
    else
        echo "❌ Neither python3.13 nor pyenv found."
        exit 1
    fi
fi

# 3️⃣ Verify version
PYTHON_ACTUAL_VERSION=$($PYTHON_BIN --version 2>&1)
if [[ "$PYTHON_ACTUAL_VERSION" != *"$PYTHON_VERSION"* ]]; then
    echo "❌ Found $PYTHON_ACTUAL_VERSION but expected Python $PYTHON_VERSION."
    exit 1
fi

echo "✅ Found correct Python version: $PYTHON_ACTUAL_VERSION"

# 4️⃣ Create virtual environment if it doesn't exist
if [[ -d "$VENV_NAME" ]]; then
    echo "⚠ Virtual environment '$VENV_NAME' already exists."
else
    echo "🚀 Creating virtual environment '$VENV_NAME'..."
    "$PYTHON_BIN" -m venv "$VENV_NAME"
fi

# 5️⃣ Activate and upgrade pip, setuptools, wheel
source "$VENV_NAME/bin/activate"
echo "⬆ Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

# 6️⃣ Install requirements if present
if [[ -f "requirements.txt" ]]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "ℹ No requirements.txt found. Skipping package install."
fi

deactivate
echo "✅ Virtual environment '$VENV_NAME' is fully set up."


