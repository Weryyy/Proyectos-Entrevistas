# 🐍 Tutorial de Python

Guía de referencia rápida para el lenguaje Python, orientada a los módulos de este repositorio.

---

## 📋 Índice

1. [Fundamentos](#1-fundamentos)
2. [Estructuras de datos](#2-estructuras-de-datos)
3. [Funciones y lambdas](#3-funciones-y-lambdas)
4. [Clases y herencia](#4-clases-y-herencia)
5. [Módulos de la stdlib útiles](#5-módulos-de-la-stdlib-útiles)
6. [Testing con pytest](#6-testing-con-pytest)
7. [Concurrencia (threads y asyncio)](#7-concurrencia-threads-y-asyncio)
8. [Recursos](#8-recursos)

---

## 1. Fundamentos

```python
# Variables y tipos básicos
nombre: str   = "Homelab"
version: int  = 3
pi: float     = 3.14159
activo: bool  = True
datos: bytes  = b"\x00\x01"

# f-strings (Python 3.6+)
print(f"Python {version} — {nombre}")

# Unpacking
a, b, *resto = [1, 2, 3, 4, 5]   # a=1, b=2, resto=[3,4,5]

# Walrus operator (Python 3.8+)
if (n := len(resto)) > 2:
    print(f"Tenemos {n} elementos extra")
```

---

## 2. Estructuras de datos

```python
# Lista (mutable, ordenada)
nums = [3, 1, 4, 1, 5, 9]
nums.sort()
nums_pares = [x for x in nums if x % 2 == 0]

# Diccionario
config = {"host": "localhost", "puerto": 8006, "ssl": True}
host = config.get("host", "127.0.0.1")   # valor por defecto

# Set
visto = {1, 2, 3}
visto.add(4)
visto.discard(2)

# Tupla (inmutable)
punto = (10.5, 20.3)
x, y = punto

# deque — cola eficiente O(1) por ambos extremos
from collections import deque
cola: deque[int] = deque(maxlen=5)
cola.appendleft(0)

# OrderedDict — mantiene orden de inserción (Python 3.7+ dict ya lo hace)
from collections import OrderedDict
od: OrderedDict[str, int] = OrderedDict()
```

---

## 3. Funciones y lambdas

```python
# Anotaciones de tipo
def saludar(nombre: str, veces: int = 1) -> str:
    return (f"Hola, {nombre}! " * veces).strip()

# *args y **kwargs
def log(*mensajes: str, nivel: str = "INFO") -> None:
    for m in mensajes:
        print(f"[{nivel}] {m}")

# Lambda
doble = lambda x: x * 2
lista = list(map(doble, range(5)))       # [0, 2, 4, 6, 8]

# Decoradores
import functools, time

def cronometrar(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        resultado = func(*args, **kwargs)
        print(f"{func.__name__} tardó {time.perf_counter()-t0:.3f}s")
        return resultado
    return wrapper

@cronometrar
def tarea_pesada(n: int) -> int:
    return sum(range(n))
```

---

## 4. Clases y herencia

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class Nodo:
    nombre: str
    cpu: float = 0.0
    memoria_gb: int = 8
    vms: list[str] = field(default_factory=list)
    _contador: ClassVar[int] = 0

    def __post_init__(self):
        Nodo._contador += 1

    @property
    def esta_sobrecargado(self) -> bool:
        return self.cpu > 0.9

    @classmethod
    def crear_minimo(cls, nombre: str) -> "Nodo":
        return cls(nombre=nombre, cpu=0.0, memoria_gb=4)

    def __repr__(self) -> str:
        return f"Nodo({self.nombre!r}, cpu={self.cpu:.0%})"


# Herencia
class NodoHA(Nodo):
    def __init__(self, nombre: str, replica_de: str):
        super().__init__(nombre)
        self.replica_de = replica_de
```

---

## 5. Módulos de la stdlib útiles

```python
# pathlib — manejo de rutas
from pathlib import Path
ruta = Path("main") / "modulo-1-lru-cache" / "codigo" / "python"
archivos_py = list(ruta.glob("*.py"))

# json
import json
datos = json.loads('{"clave": 42}')
texto = json.dumps(datos, indent=2, ensure_ascii=False)

# subprocess — ejecutar comandos externos
import subprocess
resultado = subprocess.run(["git", "log", "--oneline", "-5"],
                          capture_output=True, text=True, check=True)
print(resultado.stdout)

# itertools
import itertools
pares = list(itertools.combinations([1, 2, 3], 2))  # [(1,2),(1,3),(2,3)]
```

---

## 6. Testing con pytest

```python
# test_ejemplo.py
import pytest

def suma(a: int, b: int) -> int:
    return a + b

def test_suma_positivos():
    assert suma(2, 3) == 5

def test_suma_negativos():
    assert suma(-1, -1) == -2

@pytest.mark.parametrize("a,b,esperado", [
    (0, 0, 0),
    (1, 1, 2),
    (-1, 1, 0),
])
def test_suma_parametrizado(a, b, esperado):
    assert suma(a, b) == esperado

def test_division_por_cero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

# Ejecutar: pytest test_ejemplo.py -v
```

---

## 7. Concurrencia (threads y asyncio)

```python
# Threads (I/O bound)
import threading

def tarea(n: int) -> None:
    print(f"Hilo {n} iniciado")

hilos = [threading.Thread(target=tarea, args=(i,)) for i in range(4)]
for h in hilos: h.start()
for h in hilos: h.join()

# asyncio (I/O asíncrono)
import asyncio

async def fetch(url: str) -> str:
    await asyncio.sleep(0.1)  # simula I/O
    return f"Respuesta de {url}"

async def main():
    urls = ["http://a.com", "http://b.com", "http://c.com"]
    resultados = await asyncio.gather(*[fetch(u) for u in urls])
    for r in resultados:
        print(r)

asyncio.run(main())
```

---

## 8. Recursos

- [Documentación oficial Python 3.11](https://docs.python.org/3.11/)
- [Real Python — tutoriales prácticos](https://realpython.com/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [pytest — documentación](https://docs.pytest.org/)
