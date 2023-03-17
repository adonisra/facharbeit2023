import argparse
import subprocess
import time

from lang.lexer import Lexer
from lang.parser import Parser
from lang.ast import SymbolTable

parser = argparse.ArgumentParser(description="Compiler")
parser.add_argument("file", help="Die Datei die kompiliert werden soll")

args = parser.parse_args()

with open(args.file) as f:
    source_code = f.read()

if not source_code:
    exit()

start = time.time()
lexer = Lexer(source_code)
tokens = lexer.tokenize()
parser = Parser(tokens)
mod = parser.parse()
    
sym_table = SymbolTable()

code = mod.compile(sym_table, indent=0)

print(f"Kompiliert in {round(time.time() - start, 6)} Sekunden.")

with open("out.c", "w") as f:
    f.write(code)

subprocess.run(["gcc", "out.c", "-o", "main"])