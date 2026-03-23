# 🐚 Tutorial Básico: Bash Shell Scripting

Bash (Bourne Again SHell) es el intérprete de comandos por defecto en la mayoría de sistemas Linux. Es la herramienta fundamental para cualquier ingeniero de DevOps o SysAdmin.

---

## 🏗️ Fundamentos

### 1. El Shebang
Todo script debe empezar indicando qué intérprete usar:
```bash
#!/bin/bash
```

### 2. Variables y Tipado
En Bash no hay tipos. Todo son strings, pero podemos tratarlos como números.
```bash
NOMBRE="Archie"
EDAD=10
echo "Hola $NOMBRE, tienes $EDAD años."
```
*Nota: No dejes espacios alrededor del igual `=`.*

### 3. Argumentos y Salida
- `$0`: Nombre del script.
- `$1, $2...`: Argumentos pasados.
- `$#`: Número de argumentos.
- `$?`: Código de salida del último comando (0 es éxito).

### 4. Estructuras de Control
#### Condicionales:
```bash
if [ "$EDAD" -gt 18 ]; then
    echo "Eres mayor de edad."
else
    echo "Eres menor."
fi
```
#### Bucles:
```bash
for i in {1..5}; do
    echo "Iteración $i"
done
```

---

## 🛠️ Comandos Imprescindibles
- `grep`: Buscar texto.
- `sed`: Editar texto en flujo.
- `awk`: Procesar datos por columnas.
- `curl`: Descargar contenido de la red.
- `chmod +x`: Hacer que un script sea ejecutable.
