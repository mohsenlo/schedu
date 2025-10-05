# Schedu - The DSL for scheduling

Schedu provides a DSL for defining tasks and simple scheduling rules, helping you organize and view your weekly plans. The project is implemented in Python.

## Features

- Supports midnight-spanning tasks (tasks that start today and end tomorrow)
- Detects conflicts between new and existing tasks
- Enables batch task creation for specific days
- Displays weekly tasks graphically
- Supports adding tasks in multiple definition styles

## Getting started

### Prerequisites

- Python 3
- `git`

### Installation

1. Clone the repo:

    ```bash
    git clone https://github.com/mohsenlo/schedu
    cd schedu
    ```

2. Create and activate virtual environment:

   ```bash
   # Create virtual env
   python -m venv .venv


   # Activate venv
   
   # macOS / Linux
   source .venv/bin/activate

   # Windows (Powershell)
   .venv/Scripts/Activate.ps1
   ```

3. Install dependencies

   ```bash
   pip install -r requirements/requirements.txt

   # development
   pip install -r requirements/requirements-dev.txt
   ```

### Usage

- Run interpreter in REPL mode:

  ```bash
  python .\src\interpreter.py
  ```
