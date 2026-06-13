import ast


def validate(code: str) -> tuple[bool, str]:
    """Validate Python syntax for the given code string.

    Returns (True, "") if syntactically valid, otherwise (False, error_message).
    """
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"

