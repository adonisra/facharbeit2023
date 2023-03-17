import typing as t

__all__: t.Final[t.List[str]] = [
    "ID_VALID_START_CHARS",
    "ID_VALID_CHARS",
    "KEYWORDS"
]

ID_VALID_START_CHARS: t.Final[str] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
ID_VALID_CHARS: t.Final[str] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
KEYWORDS: t.Final[t.List[str]] = [
    "let",
    "if",
    "elif",
    "else",
    "and",
    "or",
    "not",
    "repeat"
]
