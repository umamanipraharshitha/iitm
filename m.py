from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import StringIO
import sys
import traceback
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code, {})
        output = sys.stdout.getvalue()
        return {
            "success": True,
            "output": output
        }

    except Exception:
        return {
            "success": False,
            "output": traceback.format_exc()
        }

    finally:
        sys.stdout = old_stdout


def extract_error_lines(tb: str):
    matches = re.findall(r'File "<string>", line (\d+)', tb)

    if matches:
        return [int(matches[-1])]

    return []


@app.get("/")
def home():
    return {"message": "Code Interpreter API Running"}


@app.post("/code-interpreter")
def code_interpreter(req: CodeRequest):
    result = execute_python_code(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    return {
        "error": extract_error_lines(result["output"]),
        "result": result["output"]
    }
