# Módulo 10: El Constructor de Lenguajes — Mini Compilador

## 🧠 Concepto Técnico

Un **compilador** es un programa que transforma código fuente escrito en un lenguaje
de alto nivel a otro lenguaje (generalmente de bajo nivel o código máquina). Un
**intérprete** ejecuta ese código directamente sin producir un binario separado.

Implementar un compilador o intérprete —aunque sea en miniatura— demuestra dominio
de **estructuras de datos recursivas**, **diseño de sistemas** y **pensamiento algorítmico
de alto nivel**. Por eso aparecen en entrevistas de empresas como:

| Empresa      | Por qué importa                                                         |
|--------------|-------------------------------------------------------------------------|
| **Google**   | V8 (JavaScript), Dart compiler, query optimizers en BigQuery            |
| **Anthropic**| DSLs internos, herramientas de evaluación de modelos de lenguaje        |
| **Apple**    | Swift compiler (open-source), LLVM contributor                          |
| **Meta**     | Hack (PHP compiler), PyTorch's TorchScript                              |
| **Amazon**   | Cedar policy language, optimizadores de consultas en Redshift           |

### Las 3 fases de un compilador/intérprete

```
Código Fuente
     │
     ▼
┌──────────┐    Tokens     ┌──────────┐     AST      ┌──────────┐   Resultado
│  LEXER   │ ────────────► │  PARSER  │ ────────────► │EVALUADOR │ ──────────►
│(tokenizer)│              │(análisis │              │(intérprete│
└──────────┘              │sintáctico)│              │  o codegen│
                          └──────────┘              └──────────┘

Fase 1: Análisis Léxico   Fase 2: Análisis           Fase 3: Evaluación /
  "let x = 42"            Sintáctico                 Generación de Código
  →  [LET, ID(x),         → AST jerárquico           → Valor o bytecode
      ASSIGN, NUM(42)]
```

---

## 🚀 Lore: El Constructor de Lenguajes

> *El Gran Consejo de la Civilización Robot te ha encomendado la tarea más
> sagrada: construir el primer lenguaje de programación para robots.*
>
> *Los robots hasta ahora solo entendían señales eléctricas. Tú debes crear
> la cadena completa: desde el texto que un robot escribe en su terminal
> hasta el resultado que aparece en su pantalla de salida.*
>
> *Primero, el Lexer romperá las palabras en átomos de significado — los
> Tokens. Luego, el Parser organizará esos átomos en una estructura de árbol
> que capture la jerarquía y el orden de las operaciones. Finalmente, el
> Intérprete recorrerá ese árbol y ejecutará cada instrucción, dando vida al
> programa.*
>
> *Esta es la trilogía del lenguaje. Domínala y los robots te llamarán
> "El Arquitecto".*

---

## 🔤 El Mini-Lenguaje Robot

El lenguaje soporta las siguientes construcciones:

### Tipos de datos

| Tipo      | Ejemplo          | Descripción              |
|-----------|------------------|--------------------------|
| Entero    | `42`, `-7`       | Número sin punto decimal |
| Flotante  | `3.14`, `-0.5`   | Número con punto decimal |
| Booleano  | `true`, `false`  | Valor lógico             |

### Operadores

| Categoría      | Operadores           | Ejemplo            |
|----------------|----------------------|--------------------|
| Aritmética     | `+` `-` `*` `/`      | `10 + 3 * 2`       |
| Comparación    | `==` `!=` `<` `>` `<=` `>=` | `x > 5`  |
| Agrupación     | `(` `)`              | `(1 + 2) * 3`      |

### Sentencias

```
# Declaración de variable
let x = 42
let pi = 3.14
let activo = true

# Impresión
print(x + 1)       # imprime: 43

# Condicional simple
if (x > 10) print(x)

# Condicional con rama else
if (x == 42) print(1) else print(0)

# Comentarios de una línea
# Esto es ignorado por el lexer
```

### Ejemplo completo

```
# Calcula el área de un círculo
let pi = 3.14159
let radio = 5
let area = pi * radio * radio
print(area)      # → 78.53975

# Clasifica temperatura
let temp = 37
if (temp > 36) print(1) else print(0)  # → 1
```

---

## 🔑 Pipeline Detallado

```
Código fuente: "let x = 10 + 2 * 3"
                         │
                ┌────────▼────────┐
                │     LEXER       │
                │  (lexer.py)     │
                └────────┬────────┘
                         │
               ┌─────────▼──────────┐
               │      TOKENS        │
               │  LET  ID(x)  =     │
               │  NUM(10)  +        │
               │  NUM(2)  *  NUM(3) │
               └─────────┬──────────┘
                         │
                ┌────────▼────────┐
                │     PARSER      │
                │  (parser.py)    │
                └────────┬────────┘
                         │
               ┌─────────▼──────────┐
               │        AST         │
               │  Assign('x',       │
               │    BinaryOp('+',   │
               │      Number(10),   │
               │      BinaryOp('*', │
               │        Number(2),  │
               │        Number(3))) │
               └─────────┬──────────┘
                         │
                ┌────────▼────────┐
                │  INTÉRPRETE     │
                │(interpreter.py) │
                └────────┬────────┘
                         │
               ┌─────────▼──────────┐
               │     RESULTADO      │
               │  x = 16            │
               │  (10 + 2×3 = 16)   │
               └────────────────────┘
```

---

## 🏷 Tabla de Tipos de Token

| TokenType    | Símbolo / Texto  | Descripción                        |
|--------------|------------------|------------------------------------|
| `NUMBER`     | `42`, `3.14`     | Literal numérico (int o float)     |
| `BOOLEAN`    | `true`, `false`  | Literal booleano                   |
| `IDENTIFIER` | `x`, `radio`     | Nombre de variable                 |
| `PLUS`       | `+`              | Suma                               |
| `MINUS`      | `-`              | Resta / unario negativo            |
| `STAR`       | `*`              | Multiplicación                     |
| `SLASH`      | `/`              | División                           |
| `ASSIGN`     | `=`              | Asignación                         |
| `EQUAL`      | `==`             | Comparación de igualdad            |
| `NOT_EQUAL`  | `!=`             | Comparación de desigualdad         |
| `LESS`       | `<`              | Menor que                          |
| `GREATER`    | `>`              | Mayor que                          |
| `LESS_EQ`    | `<=`             | Menor o igual que                  |
| `GREATER_EQ` | `>=`             | Mayor o igual que                  |
| `LPAREN`     | `(`              | Paréntesis izquierdo               |
| `RPAREN`     | `)`              | Paréntesis derecho                 |
| `COMMA`      | `,`              | Coma (separador)                   |
| `NEWLINE`    | `\n`             | Fin de línea (separador de stmts)  |
| `LET`        | `let`            | Declaración de variable            |
| `IF`         | `if`             | Condicional                        |
| `ELSE`       | `else`           | Rama alternativa                   |
| `PRINT`      | `print`          | Impresión de valor                 |
| `EOF`        | —                | Fin del archivo                    |

---

## 🌳 Tabla de Nodos del AST

| Nodo AST    | Campos                              | Ejemplo de código          |
|-------------|-------------------------------------|----------------------------|
| `Program`   | `statements: List[Any]`             | (raíz del árbol)           |
| `Number`    | `value: int`                        | `42`                       |
| `Float`     | `value: float`                      | `3.14`                     |
| `Boolean`   | `value: bool`                       | `true`                     |
| `Variable`  | `name: str`                         | `x`                        |
| `BinaryOp`  | `left, op: str, right`              | `x + 5`, `a == b`          |
| `UnaryOp`   | `op: str, operand`                  | `-x`                       |
| `Assign`    | `name: str, value`                  | `let x = 10`               |
| `If`        | `condition, then_body, else_body`   | `if (x > 0) print(x)`      |
| `Print`     | `expr`                              | `print(42)`                |

---

## ⚙️ Análisis de Complejidad

| Componente   | Operación              | Tiempo   | Espacio  | Notas                              |
|--------------|------------------------|----------|----------|------------------------------------|
| **Lexer**    | `tokenize()`           | O(n)     | O(n)     | n = longitud del código fuente     |
| **Parser**   | `parse()`              | O(n)     | O(d)     | d = profundidad máxima del AST     |
| **Intérprete** | `evaluate()`         | O(n)     | O(d + v) | v = número de variables en scope   |
| **Environment** | `get()` / `set()`  | O(s)     | O(v)     | s = profundidad de ámbitos anidados|
| **Pipeline completo** | `run()`      | O(n)     | O(n)     | Lineal en el tamaño del programa   |

> **Nota:** La complejidad del intérprete es O(n) en el tamaño del AST, que a su
> vez es O(n) en el tamaño del código fuente para este subconjunto del lenguaje.

---

## 🧩 Arquitectura de Ámbitos (Scoping)

```
Entorno Global
  ├── x = 10
  ├── y = 20
  └── (if branch) → Entorno Hijo
        ├── parent → Entorno Global
        └── temp = 5   ← visible solo en este bloque

Búsqueda de variable 'x' desde el hijo:
  Hijo._vars → no existe
  Hijo.parent.get('x') → ¡encontrado! = 10
```

---

## ▶️ Cómo Ejecutar

### Requisitos

- Python 3.10+
- pytest (`pip install pytest`)

### Correr los tests

```bash
cd main/modulo-10-mini-compilador/codigo
pytest test_interpreter.py -v
```

### Usar el intérprete de forma interactiva

```python
from interpreter import Interpreter

interp = Interpreter()

# Ejecutar código del lenguaje robot
interp.run("let radio = 5")
interp.run("let pi = 3.14159")
interp.run("let area = pi * radio * radio")
interp.run("print(area)")

# Las variables persisten entre llamadas
print(interp.global_env.get('area'))  # 78.53975

# Ver todas las salidas capturadas
print(interp.output)  # ['78.53975']
```

### Demo rápida

```bash
cd main/modulo-10-mini-compilador/codigo
python -c "
from interpreter import Interpreter
i = Interpreter()
i.run('let x = 10\nlet y = 32\nprint(x + y)')
"
# Salida: 42
```

---

## 📁 Estructura del Módulo

```
modulo-10-mini-compilador/
├── README.md               ← Este archivo
├── mapa-mental.md          ← Mapa conceptual y ruta de estudio
└── codigo/
    ├── lexer.py            ← Fase 1: Analizador Léxico (tokenizer)
    ├── parser.py           ← Fase 2: Analizador Sintáctico (AST builder)
    ├── interpreter.py      ← Fase 3: Intérprete de árbol (tree-walker)
    └── test_interpreter.py ← Suite de tests con pytest (68 tests)
```

---

## 🎯 Preguntas de Entrevista Frecuentes

1. **¿Cuál es la diferencia entre un compilador y un intérprete?**
   Un compilador traduce el programa completo a otro lenguaje antes de ejecutarlo.
   Un intérprete lo ejecuta línea a línea (o nodo a nodo en el AST) directamente.

2. **¿Qué es un árbol de sintaxis abstracta (AST)?**
   Una representación en forma de árbol del código fuente que captura la estructura
   semántica (no la sintáctica). Las hojas son literales/variables; los nodos
   internos son operaciones o sentencias.

3. **¿Por qué usar descenso recursivo para el parser?**
   Es simple, legible y mapea directamente a la gramática BNF. Es O(n) para
   gramáticas LL(k) sin ambigüedad, y es fácil de depurar.

4. **¿Cómo funcionan los ámbitos léxicos (lexical scoping)?**
   Cada bloque crea un nuevo entorno hijo que apunta a su entorno padre.
   La búsqueda de variables sube por la cadena de padres hasta encontrarla
   o lanzar un error si no existe.

5. **¿Cómo extenderías este intérprete para soportar funciones?**
   Añadirías un nodo `FunctionDef` al AST, un `TokenType.FUNC`, y en el
   intérprete guardarías el nodo en el entorno. Al llamar la función,
   crearías un nuevo `Environment` con las variables de los parámetros.
