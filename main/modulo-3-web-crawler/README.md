# Módulo 3: El Rastreador Cortés — Web Crawler

## 🕷️ Misión del Agente

Eres un agente secreto de inteligencia artificial, un rastreador cortés cuya misión es
**mapear la red completa de un sitio web objetivo**. Pero a diferencia de los crawlers
bárbaros que bombardean servidores sin piedad, tú eres diplomático:

- 🎩 **Nunca abrumas al servidor** — usas un *semáforo* para controlar cuántas peticiones
  simultáneas realizas (rate limiting por concurrencia).
- 🗺️ **No dejas página sin visitar** — recorres el grafo web usando BFS (Breadth-First Search),
  explorando nivel por nivel.
- 🔒 **Nunca visitas la misma página dos veces** — tu *visited set* (conjunto de visitados)
  es tu memoria perfecta.

> *"Un buen agente no deja rastro... excepto un mapa perfecto del territorio enemigo."*

---

## 🧠 Explicación Técnica

### Estructuras de Datos Clave

| Estructura | Propósito | Complejidad |
|---|---|---|
| **Cola BFS (Queue)** | Mantiene las URLs pendientes por visitar, en orden FIFO | O(1) enqueue/dequeue |
| **Visited Set** | Conjunto hash que registra URLs ya procesadas | O(1) lookup/insert |
| **Semáforo** | Controla el número máximo de peticiones concurrentes | O(1) acquire/release |
| **Site Map** | Mapa de URL → {links, título} que representa el grafo descubierto | O(1) insert/lookup |

### Algoritmo: BFS sobre el Grafo Web

```
1. Encolar la URL semilla (startUrl)
2. Mientras la cola no esté vacía Y no hayamos alcanzado maxPages:
   a. Desencolar la siguiente URL
   b. Si ya fue visitada → saltar
   c. Marcar como visitada en el visited set
   d. Adquirir permiso del semáforo (esperar si hay muchas concurrentes)
   e. Hacer fetch de la página
   f. Liberar permiso del semáforo
   g. Extraer links del HTML
   h. Encolar los links no visitados
   i. Guardar en el site map: URL → {links encontrados, título}
3. Retornar el site map completo
```

### ¿Por qué BFS y no DFS?

BFS explora **nivel por nivel**, lo que significa que primero visita todas las páginas a
1 click de distancia, luego las de 2 clicks, etc. Esto es ideal para un crawler porque:

- Descubre la estructura jerárquica del sitio
- Las páginas más importantes (cercanas a la raíz) se visitan primero
- Es más predecible para rate limiting

### El Semáforo: Tu Arma de Cortesía

Un semáforo es un mecanismo de sincronización que permite controlar el acceso concurrente
a un recurso compartido (en este caso, el servidor web).

```
Semáforo(3) → permite máximo 3 peticiones simultáneas

Agente 1: acquire() ✅ (permisos restantes: 2)
Agente 2: acquire() ✅ (permisos restantes: 1)
Agente 3: acquire() ✅ (permisos restantes: 0)
Agente 4: acquire() ⏳ (espera... sin permisos disponibles)
Agente 1: release() → Agente 4: ✅ (ahora puede continuar)
```

---

## 📊 Análisis de Complejidad

| Operación | Tiempo | Espacio |
|---|---|---|
| **BFS completo** | O(V + E) | O(V) |
| **Visited set lookup** | O(1) amortizado | O(V) |
| **Visited set insert** | O(1) amortizado | — |
| **Semaphore acquire/release** | O(1) | O(K) donde K = waiters |
| **URL normalization** | O(L) donde L = longitud URL | O(L) |

Donde:
- **V** = número de páginas (vértices del grafo)
- **E** = número de enlaces (aristas del grafo)

---

## 🚀 Cómo Ejecutar

### Requisitos
- Node.js 18+ (usa módulos built-in, **sin dependencias externas**)

### Ejecutar la demo
```bash
cd main/modulo-3-web-crawler/codigo/javascript
node crawler.js
```

### Ejecutar los tests
```bash
cd main/modulo-3-web-crawler/codigo/javascript
node --test test_crawler.js
```

O con npm:
```bash
cd main/modulo-3-web-crawler/codigo/javascript
npm test
```

---

## 🧪 Tests Incluidos

| Test | Qué verifica |
|---|---|
| BFS traversal visits all reachable pages | Que el crawler encuentra todas las páginas alcanzables |
| Visited set prevents duplicate visits | Que ninguna página se visita más de una vez |
| Semaphore limits concurrency | Que el semáforo respeta el límite de concurrencia |
| Handles circular links without infinite loop | Que los ciclos no causan loops infinitos |
| Respects maxPages limit | Que se detiene al alcanzar el máximo de páginas |
| URL normalization works correctly | Que las URLs se normalizan correctamente |
| Generates correct site map | Que el mapa del sitio refleja el grafo real |
| Handles dead-end pages gracefully | Que las páginas sin enlaces se manejan bien |

---

## 📁 Estructura de Archivos

```
modulo-3-web-crawler/
├── README.md              ← Este archivo
└── codigo/
    └── javascript/
        ├── package.json   ← Configuración del proyecto
        ├── crawler.js     ← Implementación del crawler
        └── test_crawler.js ← Suite de tests
```
