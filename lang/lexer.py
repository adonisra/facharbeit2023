from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import typing as t

from lang.consts import *

class TokenType(Enum):
    LET         = "let"
    IF          = "if"
    ELIF        = "elif"
    ELSE        = "else"
    ID          = "ID"
    STRING      = "STRING"
    INT         = "INT"
    REPEAT      = "repeat"

    L_BRACE     = "{"
    R_BRACE     = "}"
    L_PAREN     = "("
    R_PAREN     = ")"

    LT          = "<"
    GT          = ">"
    EQUAL       = "="

    PLUS        = "+"
    MINUS       = "-"
    MUL         = "*"
    DIV         = "/"

    SEMICOLON   = ";"
    COLON       = ":"
    TERNARY     = "?"


    @classmethod
    def get(cls, value: str) -> t.Optional[TokenType]:
        try:
            return cls(value)
        
        except ValueError:
            return None

T = t.TypeVar("T", bound=TokenType)

@dataclass(frozen=True)
class Token(t.Generic[T]):
    type: T
    value: t.Any
    line: int
    col: int

class Lexer:
    def __init__(self, source_code: str) -> None:
        self.source_code = source_code
        self.pos: int = 0
        self.char: str = self.source_code[self.pos]

        self.line: int = 1
        self.column: int = 1

    def advance(self) -> None:
        if self.char == "\n":
            self.line += 1
            self.column = 1

        self.pos += 1
        self.column += 1

        if self.pos >= len(self.source_code):
            self.char = None

        else:
            self.char = self.source_code[self.pos]

    def skip_whitespace(self) -> None:
        while self.char and self.char.isspace():
            self.advance()

    def skip_comment(self) -> None:
        while self.char and self.char != "\n":
            self.advance()

    def get_chars(
        self, *, condition: t.Callable[[str], bool]
    ) -> t.Generator[str, None, None]:
        while (
            self.char is not None
            and condition(self.char)
        ):
            yield self.char
            self.advance()

    def tokenize(self) -> t.Union[t.List[Token], t.NoReturn]:
        tokens: t.List[Token] = []

        while self.char is not None:
            line = self.line
            column = self.column

            if self.char.isdigit():
                integer: str = "".join(self.get_chars(
                    condition=lambda c: c.isdigit()
                ))
                tokens.append(Token(
                    TokenType.INT, int(integer),
                    line=line,
                    col=column
                ))

            elif self.char in ID_VALID_START_CHARS:
                identifier = "".join(self.get_chars(
                    condition=lambda c: c in ID_VALID_CHARS
                ))
                t_type: TokenType = TokenType.ID

                if identifier in KEYWORDS:
                    t_type = TokenType.get(identifier)

                tokens.append(Token(
                    t_type, identifier,
                    line=line,
                    col=column
                ))

            elif t_type := TokenType.get(self.char):
                self.advance()
                tokens.append(Token(
                    t_type, t_type.value,
                    line=line,
                    col=column
                ))

            elif self.char.isspace():
                self.skip_whitespace()

            elif self.char == "#":
                self.skip_comment()

            else:
                raise ValueError(f"{self.char!r} wird nicht akzeptiert ({line}:{column})")

        return tokens
