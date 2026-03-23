# 🟨 Tutorial de JavaScript (Node.js)

Guía de referencia rápida para JavaScript/Node.js, orientada a los módulos de este repositorio.

---

## 📋 Índice

1. [Fundamentos modernos (ES2022+)](#1-fundamentos-modernos-es2022)
2. [Funciones y closures](#2-funciones-y-closures)
3. [Clases y prototipos](#3-clases-y-prototipos)
4. [Asincronía — Promises y async/await](#4-asincronía--promises-y-asyncawait)
5. [Módulos ES y CommonJS](#5-módulos-es-y-commonjs)
6. [Node.js — APIs clave](#6-nodejs--apis-clave)
7. [Testing con node:test](#7-testing-con-nodetest)
8. [Recursos](#8-recursos)

---

## 1. Fundamentos modernos (ES2022+)

```javascript
// Variables: const > let, nunca var
const PI = 3.14159;
let contador = 0;

// Destructuring
const [primero, segundo, ...resto] = [1, 2, 3, 4];
const { host = "localhost", puerto = 8080 } = config;

// Optional chaining (?.) y nullish coalescing (??)
const nombre = usuario?.perfil?.nombre ?? "Anónimo";

// Logical assignment
config.timeout ??= 5000;   // asigna solo si es null/undefined
config.debug   ||= false;  // asigna solo si es falsy

// Template literals
const msg = `Conectando a ${host}:${puerto}...`;

// Object shorthand
const x = 10, y = 20;
const punto = { x, y };   // { x: 10, y: 20 }
```

---

## 2. Funciones y closures

```javascript
// Arrow functions
const doble = x => x * 2;
const suma  = (a, b) => a + b;

// Parámetros rest y default
function log(nivel = "INFO", ...mensajes) {
    mensajes.forEach(m => console.log(`[${nivel}] ${m}`));
}

// Closure — contador privado
function crearContador(inicio = 0) {
    let count = inicio;
    return {
        incrementar: () => ++count,
        valor: () => count,
        reset: () => { count = inicio; }
    };
}

const c = crearContador(10);
console.log(c.incrementar()); // 11

// Higher-order functions
const numeros = [1, 2, 3, 4, 5, 6];
const pares   = numeros.filter(n => n % 2 === 0);
const cuadrados = numeros.map(n => n ** 2);
const suma_total = numeros.reduce((acc, n) => acc + n, 0);
```

---

## 3. Clases y prototipos

```javascript
class Crawler {
    #visitadas = new Set();   // campo privado (ES2022)
    #cola = [];

    constructor(baseUrl, { concurrencia = 5 } = {}) {
        this.baseUrl = baseUrl;
        this.concurrencia = concurrencia;
    }

    get estadisticas() {
        return {
            visitadas: this.#visitadas.size,
            pendientes: this.#cola.length
        };
    }

    encolar(url) {
        if (!this.#visitadas.has(url)) {
            this.#cola.push(url);
        }
        return this;  // chaining
    }

    static normalizar(url) {
        return new URL(url).href.replace(/\/$/, "");
    }
}

// Herencia
class CrawlerRespetuoso extends Crawler {
    constructor(baseUrl, delayMs = 1000) {
        super(baseUrl, { concurrencia: 1 });
        this.delayMs = delayMs;
    }

    async esperar() {
        return new Promise(res => setTimeout(res, this.delayMs));
    }
}
```

---

## 4. Asincronía — Promises y async/await

```javascript
// Promise básica
function fetchConTimeout(url, ms = 5000) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error("Timeout")), ms);
        fetch(url)
            .then(res => { clearTimeout(timer); resolve(res.json()); })
            .catch(err => { clearTimeout(timer); reject(err); });
    });
}

// async/await con manejo de errores
async function crawlPagina(url) {
    try {
        const datos = await fetchConTimeout(url, 3000);
        return datos;
    } catch (err) {
        console.error(`[ERROR] ${url}: ${err.message}`);
        return null;
    }
}

// Promise.allSettled — no falla si alguna promesa rechaza
async function crawlVarios(urls) {
    const resultados = await Promise.allSettled(urls.map(crawlPagina));
    return resultados
        .filter(r => r.status === "fulfilled" && r.value !== null)
        .map(r => r.value);
}

// Iteradores asíncronos (streams)
async function* generarUrls(base, paginas) {
    for (let i = 1; i <= paginas; i++) {
        yield `${base}?page=${i}`;
        await new Promise(r => setTimeout(r, 100));
    }
}
```

---

## 5. Módulos ES y CommonJS

```javascript
// ESM (package.json → "type": "module")
import { EventEmitter } from "node:events";
import path from "node:path";
export { Crawler, CrawlerRespetuoso };
export default function main() { /* ... */ }

// CommonJS (legacy)
const { EventEmitter } = require("events");
module.exports = { Crawler };

// Importación dinámica (ambos sistemas)
const modulo = await import("./plugin.js");
```

---

## 6. Node.js — APIs clave

```javascript
import { readFile, writeFile, readdir } from "node:fs/promises";
import { createReadStream }             from "node:fs";
import { createInterface }              from "node:readline";
import { createServer }                 from "node:http";
import path                             from "node:path";
import { EventEmitter }                 from "node:events";

// Leer fichero línea por línea (streams, bajo consumo de memoria)
async function procesarLineas(rutaFichero) {
    const rl = createInterface({
        input: createReadStream(rutaFichero),
        crlfDelay: Infinity,
    });
    for await (const linea of rl) {
        console.log(linea);
    }
}

// Servidor HTTP mínimo
const server = createServer((req, res) => {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, path: req.url }));
});
server.listen(3000);
```

---

## 7. Testing con node:test

```javascript
// test_crawler.js
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { Crawler } from "./crawler.js";

describe("Crawler", () => {
    let crawler;

    before(() => {
        crawler = new Crawler("https://ejemplo.com");
    });

    it("encolar agrega URL nueva", () => {
        crawler.encolar("https://ejemplo.com/pagina-1");
        assert.equal(crawler.estadisticas.pendientes, 1);
    });

    it("encolar ignora duplicados", () => {
        crawler.encolar("https://ejemplo.com/pagina-1");
        assert.equal(crawler.estadisticas.pendientes, 1);
    });

    it("normalizar quita barra final", () => {
        assert.equal(
            Crawler.normalizar("https://ejemplo.com/"),
            "https://ejemplo.com"
        );
    });
});

// Ejecutar: node --test test_crawler.js
```

---

## 8. Recursos

- [MDN JavaScript — referencia completa](https://developer.mozilla.org/es/docs/Web/JavaScript)
- [Node.js — documentación oficial](https://nodejs.org/docs/latest/api/)
- [JavaScript.info — tutorial moderno](https://javascript.info/)
- [node:test — guía integrada](https://nodejs.org/api/test.html)
