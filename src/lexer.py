import re

# This is token names and patterns for tokenizing, order of patterns is IMPORTANT! first pattern will match.
TOKEN_SPEC = [
    ("DRAW", r"draw"),
    ("UPDATE", r"update"),
    ("RENAME", r"rename"),
    ("PRINT", r"print"),
    ("TASK", r"task"),
    ("FROM", r"from"),
    ("TO", r"\bto\b"),
    ("AT", r"\bat\b"),
    ("DURATION", r"duration"),
    ("AFTER", r"after"),
    ("IN", r"\bin\b"),
    ("TODAY", r"today"),
    ("WEEK_DAY", r"saturday|sunday|monday|tuesday|wednesday|thursday|friday"),
    ("AND", r"and"),
    ("TIME", r"\d{2}:\d{2}"),
    ("STRING", r'"[^"]*"'),
    ("OPEN_CURLY_BRACKET", r"{"),
    ("CLOSE_CURLY_BRACKET", r"}"),
    ("SKIP", r"\s"),
    # First for mismatch word, second for any mismatch character
    ("MISMATCH", r"\b\w+\b|.+"),
]

TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC), re.IGNORECASE
)


def get_code_snippet_with_location(code: str, index):
    """return line number, position and snippet code of error with given index."""
    # count lines with get number of \n occurrence in code until index
    line = code.count("\n", 0, index) + 1
    # position index of error on that line
    col = index - code.rfind("\n", 0, index) - 1
    # which line error occurred
    snippet = code.split("\n")[line - 1]
    return (snippet, line, col)


def tokenize(code):
    n = len(code)
    pos = 0
    while pos < n:
        # get first token that match start from pos
        token = TOKEN_REGEX.match(code, pos)

        if not token:
            snippet, line, col = get_code_snippet_with_location(code, pos)
            raise SyntaxError(
                f"Tokenizing failed!!! Invalid token is: {value!r} !!\n In line {line}:>\t{snippet!r}\tat {col}"
            )

        # get token name and value
        kind = token.lastgroup
        value = token.group()

        if kind == "SKIP":
            # if token is whitespace, new line, ... go to next token and do nothing
            pass
        elif kind == "MISMATCH":
            # this is last pattern, mean token dont match with our grammar
            snippet, line, col = get_code_snippet_with_location(code, pos)
            raise SyntaxError(
                f"Unexpected character {value!r} !!!\n In line {line}:>\t{snippet!r}\tat {col}"
            )
        else:
            if kind == "STRING":
                value = value.strip('"')
            elif kind in (
                "DRAW",
                "UPDATE",
                "RENAME",
                "PRINT",
                "TASK",
                "FROM",
                "TO",
                "AT",
                "DURATION",
                "AFTER",
                "IN",
                "TODAY",
                "WEEK_DAY",
                "AND",
            ):
                value = value.lower()

            yield (kind, value)

        pos = token.end()
