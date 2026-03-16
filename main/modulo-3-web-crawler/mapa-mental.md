# 🕷 Mapa Mental — Web Crawler & Concurrencia

## ⏱ Tiempo estimado: 10–14 horas

```
                      ╔══════════════════════════╗
                      ║     WEB  CRAWLER  &      ║
                      ║     CONCURRENCIA         ║
                      ╚════════════╤═════════════╝
                                   │
       ┌──────────────┬────────────┼──────────┬────────────────┐
       ▼              ▼            ▼          ▼                ▼
 ┌───────────┐ ┌────────────┐ ┌────────┐ ┌──────────┐  ┌────────────┐
 │PREREQUISI-│ │ CONCEPTOS  │ │  RUTA  │ │ RECURSOS │  │ SIGUIENTES │
 │   TOS     │ │   CLAVE    │ │  DE    │ │          │  │   PASOS    │
 └─────┬─────┘ └─────┬──────┘ │ESTUDIO │ └────┬─────┘  └─────┬──────┘
       │              │        └───┬────┘      │              │
       ▼              ▼            ▼           ▼              ▼
```

---

## 📋 Prerequisitos

```
  Prerequisitos
  ├── JavaScript / Node.js
  │   ├── async / await
  │   ├── Promises
  │   └── Módulos (import/require)
  ├── HTTP básico
  │   ├── Métodos: GET, POST
  │   ├── Códigos de estado (200, 301, 404, 429)
  │   └── Headers (User-Agent, Content-Type)
  └── Conceptos de red
      ├── DNS (resolución de dominios)
      └── URLs (protocolo, host, path, query)
```

## 🔑 Conceptos Clave

```
  Conceptos Clave
  ├── BFS (Breadth-First Search)
  │   ├── Cola FIFO para URLs pendientes
  │   └── Recorrido nivel por nivel
  ├── Visited Set (conjunto de visitados)
  │   ├── Evitar visitar la misma URL dos veces
  │   └── Normalización de URLs
  ├── Semáforo (Semaphore)
  │   ├── Limita concurrencia máxima
  │   ├── acquire() → espera si lleno
  │   └── release() → libera un slot
  ├── Rate Limiting
  │   ├── Respetar robots.txt
  │   ├── Delays entre requests
  │   └── Backoff exponencial ante 429
  ├── URLs y Parsing
  │   ├── URL relativa → absoluta
  │   ├── Filtrar URLs externas
  │   └── Evitar trampas (query params infinitos)
  └── DNS y Resolución
      ├── Cachear resoluciones DNS
      └── Manejar timeouts
```

## 🗺 Ruta de Estudio

```
  ① HTTP Requests en Node.js
  │   └── → fetch / axios, manejar respuestas y errores
  │
  ② BFS en grafos
  │   └── → Cola de URLs, visitados, profundidad máxima
  │
  ③ Concurrencia en JavaScript
  │   ├── → Event loop, Promise.all, Promise.allSettled
  │   └── → Diferencia: paralelismo vs concurrencia
  │
  ④ Semáforos y rate limiting
  │   ├── → Implementar semáforo con Promises
  │   └── → Limitar requests por segundo
  │
  ⑤ Crawler completo
      ├── → Combinar BFS + concurrencia + semáforo
      ├── → Extraer links del HTML (cheerio / regex)
      ├── → Manejar errores gracefully
      └── → Tests con servidor mock
```

## 📚 Recursos

```
  Recursos
  ├── MDN — Fetch API
  ├── Node.js docs — async/await, Event Loop
  ├── "Web Scraping with Node.js" — tutorial práctico
  ├── robots.txt — especificación
  └── Cheerio — documentación (parsing HTML)
```

## 🚀 Siguientes Pasos

```
  Después de dominar Web Crawler →
  ├── Scrapy (framework de crawling en Python)
  ├── Puppeteer / Playwright
  │   └── → Crawling de SPAs con JavaScript
  ├── Generadores de sitemaps
  ├── Herramientas SEO
  │   ├── Screaming Frog
  │   └── Lighthouse
  └── Sistemas distribuidos de crawling
      └── → Múltiples workers, cola compartida (Redis)
```

---

> **💡 Consejo:** El web es un grafo gigante donde cada página es un nodo y
> cada link es una arista. Tu crawler hace BFS sobre ese grafo, pero debe ser
> educado: respeta robots.txt y no satures los servidores.
