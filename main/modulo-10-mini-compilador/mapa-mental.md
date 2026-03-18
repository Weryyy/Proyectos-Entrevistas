# 🧠 Mapa Mental — Mini Compilador / Intérprete

## ⏱ Tiempo estimado: 10–15 horas

```
                    ╔══════════════════════════════╗
                    ║     MINI COMPILADOR          ║
                    ║  (Lexer + Parser + Evaluador)║
                    ╚══════════════╤═══════════════╝
                                   │
        ┌──────────┬───────────────┼───────────────┬──────────────┐
        ▼          ▼               ▼               ▼              ▼
  ┌──────────┐ ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │PREREQUISI│ │CONCEPT.│  │FASES DEL │  │RECURSOS  │  │SIGUIENTES│
  │   TOS    │ │ CLAVE  │  │COMPILADOR│  │          │  │  PASOS   │
  └────┬─────┘ └───┬────┘  └─────┬────┘  └────┬─────┘  └────┬─────┘
       │            │             │             │             │
       ▼            ▼             ▼             ▼             ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── Python intermedio
  │   ├── Clases y dataclasses
  │   ├── Enums (enum.Enum, auto())
  │   ├── isinstance() y jerarquía de tipos
  │   └── Recursión (para el parser y el evaluador)
  ├── Estructuras de datos
  │   ├── Árboles (el AST es un árbol)
  │   ├── Pilas implícitas (call stack de la recursión)
  │   └── Diccionarios (entorno de variables)
  └── Conceptos teóricos básicos
      ├── Big-O notation (complejidad del pipeline)
      ├── Gramáticas formales (BNF / EBNF) — opcional
      └── Recursión mutua (parser llama a sí mismo)
```

---

## 🔑 Conceptos Clave

```
  Mini Compilador
  │
  ├── LEXER (Analizador Léxico)
  │   ├── Token: unidad mínima de significado
  │   │   ├── TokenType: tipo del token (NUMBER, IF, PLUS, ...)
  │   │   ├── value: valor literal (42, 'x', True, ...)
  │   │   └── line: número de línea (para errores)
  │   ├── Técnicas
  │   │   ├── Lookahead de 1 carácter (_peek)
  │   │   ├── Avanzar y consumir (_advance)
  │   │   └── Skip de espacios y comentarios
  │   └── Errores: LexerError (carácter inesperado)
  │
  ├── PARSER (Analizador Sintáctico)
  │   ├── AST (Abstract Syntax Tree)
  │   │   ├── Program → lista de sentencias
  │   │   ├── Assign  → let x = expr
  │   │   ├── If      → condition + then_body + else_body
  │   │   ├── Print   → expr
  │   │   ├── BinaryOp → left + op + right
  │   │   ├── UnaryOp  → op + operand
  │   │   └── Hojas: Number, Float, Boolean, Variable
  │   ├── Técnica: Descenso Recursivo (Recursive Descent)
  │   │   ├── Una función por regla gramatical
  │   │   ├── Precedencia: comparación < suma < mult < unario < primario
  │   │   └── Lookahead de 1 token (_current)
  │   └── Errores: ParseError (token inesperado)
  │
  ├── INTÉRPRETE (Evaluador de AST)
  │   ├── Tree-Walking Interpreter
  │   │   ├── evaluate(node) → despacha según type(node)
  │   │   └── Recursión natural sobre el árbol
  │   ├── Environment (Entorno de Variables)
  │   │   ├── _vars: Dict[str, Any] — variables del ámbito actual
  │   │   ├── parent: Environment | None — ámbito padre
  │   │   ├── get(name): sube por la cadena de padres
  │   │   └── set(name, value): siempre en el ámbito actual
  │   └── Errores semánticos
  │       ├── DivisionPorCero
  │       ├── VariableNoDefinida
  │       └── ErrorDeTipo (bool no es número)
  │
  └── PIPELINE COMPLETO
      ├── Lexer → tokens
      ├── Parser → AST
      └── Interpreter.evaluate(AST) → resultado
```

---

## 🗺 Ruta de Estudio

```
  ① Entender por qué existen los compiladores
  │   └── → ¿Cómo pasa "let x = 10" a un resultado?
  │
  ② Estudiar el Lexer (lexer.py)
  │   ├── → Leer la clase TokenType y KEYWORDS
  │   ├── → Trazar _read_number y _read_identifier
  │   ├── → Ejecutar: Lexer("let x = 42").tokenize()
  │   └── → Agregar un token nuevo (e.g., AND) como ejercicio
  │
  ③ Entender las gramáticas formales
  │   ├── → Leer el docstring de la clase Parser
  │   └── → Dibujar la gramática BNF en papel
  │
  ④ Estudiar el Parser (parser.py)
  │   ├── → Trazar _parse_additive llamando a _parse_multiplicative
  │   ├── → Ejecutar: Parser(tokens).parse() y visualizar el AST
  │   └── → Verificar la precedencia: 1 + 2 * 3 → +(1, *(2,3))
  │
  ⑤ Estudiar el Intérprete (interpreter.py)
  │   ├── → Leer evaluate() y cada rama isinstance()
  │   ├── → Trazar _eval_binary con op='+'
  │   └── → Entender Environment.get() con ámbitos anidados
  │
  ⑥ Correr los tests y analizar cada clase de test
  │   ├── TestLexer   → 17 tests del tokenizador
  │   ├── TestParser  → 14 tests del AST
  │   ├── TestInterpreter → 30 tests del evaluador
  │   └── TestIntegracion → 7 tests de pipeline completo
  │
  ⑦ Extender el lenguaje (ejercicios avanzados)
      ├── → Añadir operador % (módulo)
      ├── → Añadir strings: "hola robot"
      ├── → Añadir bucle while
      └── → Añadir funciones definidas por el usuario
```

---

## 📚 Recursos

```
  Recursos
  ├── Libros
  │   ├── "Crafting Interpreters" — Robert Nystrom (gratis en craftinginterpreters.com)
  │   │   └── El mejor recurso práctico; implementa Lox, similar a nuestro lenguaje
  │   ├── "Writing An Interpreter In Go" — Thorsten Ball
  │   │   └── Muy accesible; mismo enfoque tree-walking
  │   └── "Compilers: Principles, Techniques & Tools" — Aho, Lam, Sethi, Ullman
  │       └── El "Dragon Book"; referencia académica clásica
  │
  ├── Online
  │   ├── Let's Build A Simple Interpreter — Ruslan Spivak (blog)
  │   ├── CS143 Stanford Compilers — YouTube / Coursera
  │   └── PLZoo — Programming Language Zoo (ejemplos de mini-lenguajes)
  │
  └── Código de referencia
      ├── CPython (cpython/Python/compile.c) — el compilador de Python
      ├── MicroPython — Python embebido, código más compacto
      └── Lox en Java/C — repositorio oficial de Crafting Interpreters
```

---

## 🚀 Siguientes Pasos

```
  Después de dominar el Mini Compilador →
  │
  ├── Añadir más construcciones al lenguaje
  │   ├── Strings y concatenación
  │   ├── Bucles: while / for
  │   ├── Funciones de primera clase
  │   └── Arrays / listas
  │
  ├── Compiladores reales
  │   ├── LLVM (backend de Clang, Rust, Swift)
  │   │   └── Aprende a emitir LLVM IR desde Python
  │   ├── Bytecode + Máquina Virtual
  │   │   ├── Compilar AST a bytecode (como CPython)
  │   │   └── Implementar un stack-based VM
  │   └── JIT Compilation
  │       └── PyPy, LuaJIT — compilar en tiempo de ejecución
  │
  ├── Análisis estático
  │   ├── Type checker sobre el AST
  │   ├── Linters (detectar variables no usadas)
  │   └── Optimizaciones (constant folding: 2*3 → 6 en el AST)
  │
  └── Aplicaciones prácticas en entrevistas
      ├── Evaluar expresiones matemáticas (LeetCode 224, 227, 772)
      ├── Parsear JSON / XML manualmente
      ├── Implementar una calculadora con precedencia
      └── DSL para configuración (como HCL de Terraform)
```

---

> **💡 Consejo:** Para dominar el parser, dibuja el árbol de llamadas a mano para
> la expresión `1 + 2 * 3`. Verás cómo la recursión natural del descenso
> resuelve la precedencia sin tablas explícitas. ¡Es el momento "eureka" del módulo!
