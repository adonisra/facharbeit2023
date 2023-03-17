from __future__ import annotations

import abc
import functools
import random
import typing as t

from lang.consts import ID_VALID_START_CHARS

if t.TYPE_CHECKING:
    T = t.TypeVar("T", bound=int)

_id_gen = functools.partial(functools.partial(random.sample, ID_VALID_START_CHARS, 6))

ARITHMETIC_OP_MAPPINGS: t.Dict[str, t.Callable[[int, int], int]] = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y
}

COMP_OP_MAPPINGS: t.Dict[str, t.Callable[[int, int], bool]] = {
    ">": lambda x, y: x > y,
    "<": lambda x, y: x < y
}

class LogMixin:
    standalone: bool = False

    def log(self, value: T) -> T:
        if self.standalone is True:
            print(value)

        return value

class Node(abc.ABC):
    @abc.abstractmethod
    def eval(self, env: SymbolTable) -> t.Any:
        ...

    @abc.abstractmethod
    def compile(self, env: SymbolTable, indent: int) -> str:
        ...

class Module(Node):
    def __init__(self, statements: t.List[Node]) -> None:
        self.statements = statements
    
    def eval(self, env: SymbolTable) -> None:
        for statement in self.statements:
            statement.eval(env)

    def compile(self, env: SymbolTable, indent: int) -> str:
        code = "#include <stdio.h>\n#include <time.h>\n\nint main() {\n"
        indent += 4
        code += ' ' * indent + "clock_t start_time = clock();\n"
        for statement in self.statements:
            code += statement.compile(env, indent) + "\n"

        lines = [
            "double elapsed_time = (double)(clock() - start_time) / CLOCKS_PER_SEC;\n",
            "printf(\"Ausgeführt in %f Sekunden.\\n\", elapsed_time);\n",
            "return 0;\n"
        ]

        code += ' ' * indent + (' ' * indent).join(lines)

        indent -= 4
        code += "}"

        return code
    

class Reference(Node, LogMixin):
    def __init__(self, name: str) -> None:
        self.name = name

    def eval(self, env: SymbolTable) -> int:
        return self.log(env.get_or_raise(self.name))
    
    def compile(self, env: SymbolTable, indent: int) -> str:
        env.get_or_raise(self.name)
        if self.standalone:
            return ' ' * indent + f"printf(\"%i\\n\", {self.name});"
        return self.name

class Literal(Node, LogMixin):
    def __init__(self, value: T) -> None:
        self.value = value
    
    def eval(self, env: SymbolTable) -> T:
        return self.log(self.value)
    
    def compile(self, env: SymbolTable, indent: int) -> str:
        if self.standalone:
            return ' ' * indent + f"printf(\"{self.value}\\n\");"
        return str(self.value)

class ArithmeticOp(Node, LogMixin):
    def __init__(self, left: Node, op: str, right: Node) -> None:
        self.left = left
        self.op = op
        self.right = right

    def eval(self, env: SymbolTable) -> int:
        return self.log(
            ARITHMETIC_OP_MAPPINGS[self.op](
                self.left.eval(env),
                self.right.eval(env)
            )
        )
    
    def compile(self, env: SymbolTable, indent: int) -> str:
        code = self.left.compile(env, indent) + f" {self.op} "
        if self.op in "*/" and getattr(self.right, "op", "None") in "+-":
            code += "(" + self.right.compile(env, indent) + ")"

        else:
            code += self.right.compile(env, indent)
        
        if self.standalone:
            return ' ' * indent + f"printf(\"%i\\n\", {code});"
        return code

class CompOp(Node):
    def __init__(self, left: Node, op: str, right: Node) -> None:
        self.left = left
        self.op = op
        self.right = right
    
    def eval(self, env: SymbolTable) -> bool:
        return COMP_OP_MAPPINGS[self.op](
            self.left.eval(env),
            self.right.eval(env)
        )
    
    def compile(self, env: SymbolTable, indent: int) -> str:
        return self.left.compile(env, indent) + f" {self.op} " + self.right.compile(env, indent)
    
class Assignment(Node):
    def __init__(self, name: str, value: Node) -> None:
        self.name = name
        self.value = value
    
    def eval(self, env: SymbolTable) -> None:
        env.add(self.name, self.value.eval(env))

    def compile(self, env: SymbolTable, indent: int) -> str:
        type = ""
        if env.symbols.get(self.name) is None:
            type = "int "
            env.add(self.name, self.value.eval(env))
            
        return f"{' ' * indent}{type}{self.name} = " + self.value.compile(env, indent) + ";"
    

class Ternary(Node):
    def __init__(
        self, 
        condition: Node, 
        if_truthy: Node, 
        if_falsy: Node
    ) -> None:
        self.condition = condition
        self.if_truthy = if_truthy
        self.if_falsy = if_falsy

    def eval(self, env: SymbolTable) -> int:
        if self.condition.eval(env):
            return self.if_truthy.eval(env)
        
        else:
            return self.if_falsy.eval(env)
        
    def compile(self, env: SymbolTable, indent: int) -> str:
        return (
            self.condition.compile(env, indent) 
            + " ? " + self.if_truthy.compile(env, indent) 
            + " : " + self.if_falsy.compile(env, indent)
        )

class IfStatement(Node):
    def __init__(
        self, 
        condition: Node,
        block: t.List[Node],
        elseif_statements: t.List[IfStatement], 
        else_block: t.List[Node]
    ) -> None:
        self.condition = condition
        self.block = block
        self.elseif_statements = elseif_statements
        self.else_block = else_block

    def eval(self, env: SymbolTable) -> bool:
        if self.condition.eval(env):
            for node in self.block:
                node.eval(env)

            return True

        for node in self.elseif_statements:
            if node.eval(env):
                return True
            
        for node in self.else_block:
            node.eval(env)

        return False
    
    def compile(self, env: SymbolTable, indent: int) -> str:
        code = f"{' ' * indent}if ({self.condition.compile(env, indent)}) {{"
        indent += 4
        for node in self.block:
            code += "\n" + node.compile(env, indent)

        indent -= 4

        code += f"\n{' ' * indent}}}"

        for node in self.elseif_statements:
            code += f"\n{' ' * indent}else " + node.compile(env, indent)

        if self.else_block:
            code += f"\n{' ' * indent}else {{"

            indent += 4

            for node in self.else_block:
                code += "\n" + node.compile(env, indent)

            indent -= 4

            code += f"\n{' ' * indent}}}"

        return code
    
class Repeat(Node):
    def __init__(self, times: Node, block: t.List[Node]) -> None:
        self.times = times
        self.block = block

    def eval(self, env: SymbolTable) -> None:
        for _ in range(self.times.eval(env)):
            for node in self.block:
                node.eval(env)

    def _new_id(self, env: SymbolTable) -> str:
        id_ = "".join(_id_gen())
        while env.symbols.get(id_) is not None:
            id_ = "".join(_id_gen())

        return id_

    def compile(self, env: SymbolTable, indent: int) -> str:
        id_ = self._new_id(env)
        code = f"{' ' * indent}for (int {id_} = 0; {id_} < {self.times.eval(env)}; {id_}++) {{"
        indent += 4
        for node in self.block:
            code += "\n" + node.compile(env, indent)

        indent -= 4

        code += f"\n{' ' * indent}}}"

        return code
            
    
K = t.TypeVar("K", bound=str)
V = t.TypeVar("V", Literal, ArithmeticOp)

class SymbolTable(t.Generic[K, V]):
    def __init__(self) -> None:
        self.symbols: t.Mapping[K, V] = {}

    def add(self, name: K, value: V) -> None:
        self.symbols[name] = value

    def get_or_raise(self, name: K) -> t.Union[t.NoReturn, V]:
        if (node := self.symbols.get(name)) is None:
            raise ValueError(f"Variable {name} not found")
        
        return node