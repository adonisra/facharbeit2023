import argparse
import time

from lang.lexer import Lexer
from lang.parser import Parser
from lang.ast import SymbolTable

parser = argparse.ArgumentParser(description="Interpreter")
parser.add_argument("file", help="Die Datei die interpretiert werden soll")

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

mod.eval(sym_table)
end = time.time()

print(f"Ausgeführt in {round(end - start, 6)} Sekunden")