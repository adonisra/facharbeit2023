from __future__ import annotations

from lang.lexer import Token, TokenType

import typing as t

if t.TYPE_CHECKING:
    from lang.ast import Node
    
    ConditionT = t.Callable[[Token], bool]

from lang import ast
from lang.utils.string import join

TOKEN_NODE_MAPPING: t.Final[t.Mapping[TokenType, Node]] = {
    TokenType.INT: ast.Literal,
    TokenType.ID: ast.Reference
}
NOT_R_BRACE_CONDITION: t.Final[ConditionT] = lambda t: t.type is not TokenType.R_BRACE

class Parser:
    def __init__(self, tokens: t.List[Token]) -> None:
        self.tokens = tokens
        self.pos: int = 0

    def get_token(self) -> t.Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        
        return None

    def eat(self, *token_types: TokenType) -> None:
        curr_token = self.get_token()

        if not curr_token:
            raise EOFError("Reached end of file")

        if curr_token.type not in token_types:
            raise ValueError(
                f"Expected {join([t.value.lower() for t in token_types], last='or')}, "
                f"got {curr_token.value!r} ({curr_token.line}:{curr_token.col})"
            )

        self.pos += 1

    def statements(
        self, 
        condition: ConditionT=lambda _: True
    ) -> t.Union[t.List[Node], t.NoReturn]:
        stats: t.List[Node] = []
        while (token := self.get_token()) and condition(token):
            t_type = token.type

            if t_type in (TokenType.INT, TokenType.ID, TokenType.L_PAREN):
                node = self.expr()
                node.standalone = True
                self.eat(TokenType.SEMICOLON)
                stats.append(node)

            elif t_type is TokenType.LET:
                node = self.assignment()
                self.eat(TokenType.SEMICOLON)
                stats.append(node)

            elif t_type is TokenType.REPEAT:
                node = self.repeat()
                stats.append(node)

            elif t_type is TokenType.IF:
                node = self.if_statement()
                stats.append(node)

            else:
                raise ValueError(
                    "Statement must be an assignment, a conditional or an expression"
                )
            
        return stats

    def parse(self) -> t.Union[ast.Module, t.NoReturn]:
        stats = self.statements()

        return ast.Module(statements=stats)
    
    def repeat(self) -> ast.Repeat:
        self.eat(TokenType.REPEAT)
        times = self.expr()
        self.eat(TokenType.L_BRACE)
        block = self.statements(condition=NOT_R_BRACE_CONDITION)
        self.eat(TokenType.R_BRACE)

        return ast.Repeat(
            times=times,
            block=block
        )
    
    def ternary(self, condition: Node=None) -> ast.IfStatement:
        condition = condition or self.comparison_expr()
        self.eat(TokenType.TERNARY)
        if_truthy = self.expr()
        self.eat(TokenType.COLON)
        if_falsy = self.expr()

        return ast.Ternary(
            condition=condition,
            if_truthy=if_truthy,
            if_falsy=if_falsy
        )
    
    def assignment(self) -> Node:
        self.eat(TokenType.LET)
        token = self.get_token()
        self.eat(TokenType.ID)
        self.eat(TokenType.EQUAL)
        value = self.comparison_expr()
        if (tern_token := self.get_token()) and tern_token.type is TokenType.TERNARY:
            value = self.ternary(condition=value)

        if isinstance(value, ast.CompOp):
            raise ValueError("Can't assign to comparison.")

        return ast.Assignment(token.value, value)
    
    def if_statement(self) -> Node:
        self.eat(TokenType.IF, TokenType.ELIF)
        condition = self.comparison_expr()
        self.eat(TokenType.L_BRACE)
        stats = self.statements(condition=NOT_R_BRACE_CONDITION)
        self.eat(TokenType.R_BRACE)
        elif_statements: t.List[ast.IfStatement] = []
        else_block: t.List[Node] = []
        while (token := self.get_token()) and token.type is TokenType.ELIF:
            elif_statements.append(self.if_statement())

        if (token := self.get_token()) and token.type is TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.L_BRACE)
            else_block = self.statements(condition=NOT_R_BRACE_CONDITION)
            self.eat(TokenType.R_BRACE)

        return ast.IfStatement(
            condition=condition,
            block=stats,
            elseif_statements=elif_statements,
            else_block=else_block
        )

    def factor(self) -> Node:
        token = self.get_token()

        if not token:
            raise ValueError

        if token.type is TokenType.L_PAREN:
            self.eat(TokenType.L_PAREN)
            expression_node = self.expr()
            self.eat(TokenType.R_PAREN)
            return expression_node

        else:
            factor = 1
            if token.type is TokenType.MINUS:
                factor = -1
                self.eat(TokenType.MINUS)

            if token.type is TokenType.PLUS:
                self.eat(TokenType.PLUS)

            token = self.get_token()

            self.eat(TokenType.INT, TokenType.ID)
            return TOKEN_NODE_MAPPING[token.type](token.value * factor)

    def mult(self) -> Node:
        node = self.factor()
        while (token := self.get_token()) and token.type in (TokenType.MUL, TokenType.DIV):
            self.eat(token.type)
            node = ast.ArithmeticOp(node, token.value, self.factor())

        return node

    def expr(self) -> Node:
        node = self.mult()
        while (token := self.get_token()) and token.type in (TokenType.PLUS, TokenType.MINUS):
            self.eat(token.type)
            node = ast.ArithmeticOp(node, token.value, self.mult())

        return node
    
    def comparison_expr(self) -> Node:
        node = self.expr()
        while (token := self.get_token()) and token.type in (TokenType.GT, TokenType.LT):
            self.eat(token.type)
            node = ast.CompOp(node, token.value, self.expr())

        return node