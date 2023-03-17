# Compiler
`python -m lang.compiler example`

# Interpreter
`python -m lang.interpreter example`

# Projekt Struktur

### **Grammar**
Grammatik der Programmiersprache

### **example**
Beispielprogramm geschrieben in der Programmiersprache

### **lang/ast.py**
Klassen für Knoten des Abstrakten Syntax Baum und Klasse für Symbol Tabelle

### **lang/consts.py**
Konstanten die für den lexer relevant sind (erlaubte schlüsselwörter etc.)

### **lang/lexer.py**
Lexer Klasse und Token/TokenType Klasse

### **lang/parser.py**
Parser zur Erzeugung vom AST

### **lang/interpreter.py**
Modul das den Interpreter ausführt

### **lang/compiler.py**
Modul das den Compiler ausführt

### **lang/utils/string.py**
Hilfreiche Funktionen für Fehlernachrichten
