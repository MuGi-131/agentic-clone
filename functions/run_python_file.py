import os
import subprocess
import sys
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run python file with optional args in a specified filepath relative to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Filepath to run python file, relative to the working directory",
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_dir = (
            os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        )

        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if target_file[-3:] != ".py":
            return f'Error: "{file_path}" is not a Python file'

        command = [sys.executable, target_file]
        if args:
            command.extend(args)

        result = subprocess.run(
            command, capture_output=True, timeout=30, text=True, cwd=working_dir_abs
        )

        parts = []
        if result.returncode != 0:
            parts.append(f"Process exited with code {result.returncode}")
        if not result.stderr and not result.stdout:
            parts.append("No output produced")
        if result.stderr:
            parts.append(f"STDERR: {result.stderr}")
        if result.stdout:
            parts.append(f"STDOUT: {result.stdout}")

        return "\n".join(parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"
