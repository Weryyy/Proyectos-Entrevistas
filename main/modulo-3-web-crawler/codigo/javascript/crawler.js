// =============================================================================
// Módulo 3: El Rastreador Cortés — Web Crawler
// =============================================================================
// Un crawler educativo que demuestra BFS, Visited Set y Semáforo.
// Implementado SOLO con módulos built-in de Node.js (sin dependencias externas).
// =============================================================================

'use strict';

// =============================================================================
// SEMÁFORO — Control de concurrencia
// =============================================================================
// Un semáforo es como un guardia en la puerta de un edificio con capacidad
// limitada. Si hay espacio (permisos disponibles), te deja pasar. Si no,
// te pone en una fila de espera hasta que alguien salga.
//
// En nuestro caso, el "edificio" es el servidor web, y los "visitantes"
// son las peticiones HTTP. No queremos bombardear al servidor con 1000
// peticiones simultáneas — eso sería descortés (y probablemente nos
// bloquearían). El semáforo garantiza que nunca excedamos un número
// máximo de peticiones concurrentes.
// =============================================================================

class Semaphore {
  /**
   * @param {number} maxConcurrent - Número máximo de permisos simultáneos.
   *   Piensa en esto como "cuántos agentes pueden estar activos al mismo tiempo".
   */
  constructor(maxConcurrent) {
    // Permisos disponibles actualmente
    this._permits = maxConcurrent;
    // Cola de espera: cada elemento es una función resolve() de una Promise
    // Cuando se libera un permiso, llamamos al primer resolve() de la cola,
    // permitiendo que ese agente en espera continúe su misión.
    this._waitQueue = [];
  }

  /**
   * Adquirir un permiso del semáforo.
   * Si hay permisos disponibles, lo toma inmediatamente.
   * Si no, espera (await) hasta que otro agente libere uno.
   *
   * Internamente funciona así:
   * 1. Si _permits > 0: decrementa y continúa (resolución inmediata)
   * 2. Si _permits === 0: crea una Promise que se resuelve cuando
   *    alguien llame a release(). La función resolve se guarda en _waitQueue.
   */
  async acquire() {
    if (this._permits > 0) {
      this._permits--;
      return;
    }
    // No hay permisos — el agente debe esperar pacientemente
    return new Promise((resolve) => {
      this._waitQueue.push(resolve);
    });
  }

  /**
   * Liberar un permiso del semáforo.
   * Si hay agentes esperando en la cola, le damos el permiso al primero
   * (FIFO — el que lleva más tiempo esperando tiene prioridad).
   * Si no hay nadie esperando, simplemente incrementamos los permisos.
   */
  release() {
    if (this._waitQueue.length > 0) {
      // Despertar al primer agente en espera
      const nextResolve = this._waitQueue.shift();
      nextResolve();
    } else {
      this._permits++;
    }
  }

  /** Permisos disponibles actualmente (útil para debugging/tests) */
  get availablePermits() {
    return this._permits;
  }

  /** Agentes en cola de espera (útil para debugging/tests) */
  get waitingCount() {
    return this._waitQueue.length;
  }
}

// =============================================================================
// MockWeb — Un "Internet" simulado para pruebas
// =============================================================================
// En lugar de hacer peticiones HTTP reales (lo cual sería impredecible en tests),
// simulamos un pequeño universo web con páginas predefinidas y enlaces entre ellas.
//
// El grafo del MockWeb por defecto se ve así:
//
//   [inicio] → [about] → [team]
//      ↓          ↓         ↓
//   [blog]    [contact]  [inicio] (¡ciclo!)
//      ↓
//   [post-1] → [post-2] → [post-1] (¡otro ciclo!)
//      ↓
//   [dead-end] (sin enlaces salientes)
//
// Esto nos permite probar: BFS, ciclos, dead-ends, y normalización de URLs.
// =============================================================================

class MockWeb {
  constructor() {
    // Mapa de URL → contenido HTML de la página
    this._pages = new Map();
    this._fetchCount = new Map(); // Contador de fetches por URL (para tests)
    this._setupDefaultSite();
  }

  /**
   * Configurar el sitio web simulado por defecto.
   * Cada página tiene un <title> y enlaces <a href="..."> a otras páginas.
   */
  _setupDefaultSite() {
    this._pages.set('https://ejemplo.com/', `
      <html>
        <head><title>Inicio - Ejemplo</title></head>
        <body>
          <h1>Bienvenido</h1>
          <a href="https://ejemplo.com/about">Sobre nosotros</a>
          <a href="https://ejemplo.com/blog">Blog</a>
        </body>
      </html>
    `);

    this._pages.set('https://ejemplo.com/about', `
      <html>
        <head><title>Sobre Nosotros</title></head>
        <body>
          <a href="https://ejemplo.com/team">Equipo</a>
          <a href="https://ejemplo.com/contact">Contacto</a>
        </body>
      </html>
    `);

    this._pages.set('https://ejemplo.com/blog', `
      <html>
        <head><title>Blog</title></head>
        <body>
          <a href="https://ejemplo.com/blog/post-1">Post 1</a>
        </body>
      </html>
    `);

    this._pages.set('https://ejemplo.com/blog/post-1', `
      <html>
        <head><title>Post 1: Primeros Pasos</title></head>
        <body>
          <a href="https://ejemplo.com/blog/post-2">Post 2</a>
          <a href="https://ejemplo.com/dead-end">Enlace muerto</a>
        </body>
      </html>
    `);

    // post-2 enlaza de vuelta a post-1 — ¡ciclo!
    this._pages.set('https://ejemplo.com/blog/post-2', `
      <html>
        <head><title>Post 2: Avanzando</title></head>
        <body>
          <a href="https://ejemplo.com/blog/post-1">Volver a Post 1</a>
        </body>
      </html>
    `);

    this._pages.set('https://ejemplo.com/team', `
      <html>
        <head><title>Nuestro Equipo</title></head>
        <body>
          <a href="https://ejemplo.com/">Volver al inicio</a>
        </body>
      </html>
    `);

    this._pages.set('https://ejemplo.com/contact', `
      <html>
        <head><title>Contacto</title></head>
        <body>
          <p>Escríbenos a hola@ejemplo.com</p>
        </body>
      </html>
    `);

    // Dead-end: página sin enlaces salientes
    this._pages.set('https://ejemplo.com/dead-end', `
      <html>
        <head><title>Fin del Camino</title></head>
        <body>
          <p>No hay más enlaces aquí. Es un callejón sin salida.</p>
        </body>
      </html>
    `);
  }

  /**
   * Simular una petición HTTP a una URL.
   * @param {string} url - La URL a "visitar"
   * @returns {Promise<{status: number, body: string}>}
   */
  async fetch(url) {
    // Registrar el fetch para verificación en tests
    this._fetchCount.set(url, (this._fetchCount.get(url) || 0) + 1);

    // Simular latencia de red (breve, para no hacer lentos los tests)
    await new Promise((resolve) => setTimeout(resolve, 5));

    const normalizedUrl = url.replace(/\/$/, '') || url;
    // Buscar la página con y sin trailing slash
    const body = this._pages.get(url) || this._pages.get(normalizedUrl) || this._pages.get(url + '/');

    if (body) {
      return { status: 200, body };
    }
    return { status: 404, body: '<html><head><title>404</title></head><body>No encontrado</body></html>' };
  }

  /** Obtener cuántas veces se hizo fetch de una URL específica */
  getFetchCount(url) {
    return this._fetchCount.get(url) || 0;
  }

  /** Obtener el total de fetches realizados */
  getTotalFetchCount() {
    let total = 0;
    for (const count of this._fetchCount.values()) {
      total += count;
    }
    return total;
  }

  /** Agregar o reemplazar una página en el sitio simulado */
  setPage(url, html) {
    this._pages.set(url, html);
  }

  /** Verificar si una URL existe en el sitio simulado */
  hasPage(url) {
    return this._pages.has(url);
  }
}

// =============================================================================
// WebCrawler — El Agente Rastreador
// =============================================================================
// El corazón de este módulo. Implementa un crawler BFS con:
// - Visited Set para evitar visitar la misma página dos veces
// - Semáforo para limitar la concurrencia
// - Site Map para registrar el grafo descubierto
// =============================================================================

class WebCrawler {
  /**
   * @param {object} options - Configuración del crawler
   * @param {number} [options.maxConcurrent=3] - Máximo de peticiones simultáneas
   * @param {number} [options.maxPages=50] - Máximo de páginas a visitar
   * @param {number} [options.delayMs=100] - Delay entre peticiones (cortesía)
   * @param {Function} [options.fetchFn] - Función de fetch personalizada (para testing)
   */
  constructor(options = {}) {
    const {
      maxConcurrent = 3,
      maxPages = 50,
      delayMs = 100,
      fetchFn = null,
    } = options;

    // --- Semáforo: controla cuántas peticiones pueden estar activas ---
    this._semaphore = new Semaphore(maxConcurrent);

    // --- Visited Set: memoria del agente, URLs ya procesadas ---
    // Usamos un Set de JavaScript que internamente usa hashing,
    // garantizando búsquedas en O(1) amortizado.
    this._visitedSet = new Set();

    // --- Site Map: el mapa que construimos del sitio ---
    // Clave: URL normalizada
    // Valor: { title: string, links: string[] }
    this._siteMap = new Map();

    // --- Cola BFS: URLs pendientes de visitar ---
    // BFS usa una cola FIFO. Aquí usamos un array con shift/push.
    // (Para producción con millones de URLs, usaríamos una cola circular
    // o linked list para evitar el O(n) de shift(), pero para fines
    // educativos esto es más claro.)
    this._queue = [];

    this._maxPages = maxPages;
    this._delayMs = delayMs;
    this._fetchFn = fetchFn;

    // Contadores para estadísticas
    this._pagesVisited = 0;
    this._errors = [];
  }

  /**
   * Método principal: iniciar el rastreo BFS desde una URL semilla.
   *
   * Algoritmo BFS (Breadth-First Search):
   * 1. Encolar la URL semilla
   * 2. Mientras haya URLs en la cola Y no hayamos excedido maxPages:
   *    a. Desencolar la siguiente URL
   *    b. Si ya la visitamos → saltar (el visited set nos protege de ciclos)
   *    c. Marcarla como visitada
   *    d. Adquirir permiso del semáforo (cortesía: no saturar el servidor)
   *    e. Fetch + extraer enlaces
   *    f. Liberar permiso del semáforo
   *    g. Encolar los enlaces nuevos (no visitados)
   * 3. Retornar el site map
   *
   * @param {string} startUrl - URL semilla para iniciar el crawl
   * @returns {Promise<Map>} El site map descubierto
   */
  async crawl(startUrl) {
    const normalizedStart = this.normalizeUrl(startUrl);
    this._queue.push(normalizedStart);

    while (this._queue.length > 0 && this._pagesVisited < this._maxPages) {
      const url = this._queue.shift();

      // Verificación O(1) en el visited set — ¿ya estuvimos aquí?
      if (this._visitedSet.has(url)) {
        continue;
      }

      // Marcar como visitada ANTES de hacer el fetch
      // (así, si otro "hilo" intenta visitarla, la verá como ya visitada)
      this._visitedSet.add(url);

      // Adquirir permiso del semáforo — ser cortés con el servidor
      await this._semaphore.acquire();

      try {
        const result = await this.fetchPage(url);

        if (result) {
          const { title, links } = result;
          // Guardar en el site map
          this._siteMap.set(url, { title, links });
          this._pagesVisited++;

          // Encolar enlaces no visitados (BFS: se procesan en orden FIFO)
          for (const link of links) {
            if (!this._visitedSet.has(link)) {
              this._queue.push(link);
            }
          }
        }
      } catch (error) {
        this._errors.push({ url, error: error.message });
      } finally {
        // Siempre liberar el semáforo, incluso si hubo error
        this._semaphore.release();
      }

      // Delay de cortesía entre peticiones
      if (this._delayMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, this._delayMs));
      }
    }

    return this._siteMap;
  }

  /**
   * Hacer fetch de una página y extraer su información.
   * Usa la función de fetch personalizada si se proporcionó (para testing),
   * o el módulo http/https nativo de Node.js.
   *
   * @param {string} url - URL de la página
   * @returns {Promise<{title: string, links: string[]}|null>}
   */
  async fetchPage(url) {
    let response;

    if (this._fetchFn) {
      // Modo testing: usar la función mock
      response = await this._fetchFn(url);
    } else {
      // Modo producción: usar http/https nativo de Node.js
      response = await this._httpFetch(url);
    }

    if (!response || response.status !== 200) {
      return null;
    }

    const html = response.body;
    const title = this._extractTitle(html);
    const links = this.extractLinks(html, url);

    return { title, links };
  }

  /**
   * Fetch HTTP nativo usando los módulos built-in de Node.js.
   * Solo se usa en modo producción (no en tests).
   */
  _httpFetch(url) {
    return new Promise((resolve, reject) => {
      const protocol = url.startsWith('https') ? require('https') : require('http');
      protocol.get(url, { timeout: 10000 }, (res) => {
        let body = '';
        res.on('data', (chunk) => { body += chunk; });
        res.on('end', () => resolve({ status: res.statusCode, body }));
        res.on('error', reject);
      }).on('error', reject);
    });
  }

  /**
   * Extraer el título de una página HTML.
   * Busca el contenido entre <title> y </title>.
   */
  _extractTitle(html) {
    const match = html.match(/<title[^>]*>(.*?)<\/title>/is);
    return match ? match[1].trim() : 'Sin título';
  }

  /**
   * Extraer todos los enlaces <a href="..."> de una página HTML.
   * Solo incluye enlaces del mismo dominio (mismo origen) para
   * mantener el crawler enfocado en un solo sitio.
   *
   * @param {string} html - Contenido HTML de la página
   * @param {string} baseUrl - URL base para resolver enlaces relativos
   * @returns {string[]} Lista de URLs normalizadas
   */
  extractLinks(html, baseUrl) {
    const links = [];
    // Regex para encontrar atributos href en etiquetas <a>
    const hrefRegex = /<a[^>]+href=["']([^"']+)["'][^>]*>/gi;
    let match;

    let baseOrigin;
    try {
      baseOrigin = new URL(baseUrl).origin;
    } catch {
      return links;
    }

    while ((match = hrefRegex.exec(html)) !== null) {
      const href = match[1];

      // Ignorar enlaces especiales (javascript:, mailto:, tel:, #)
      if (/^(javascript:|mailto:|tel:|#)/.test(href)) {
        continue;
      }

      try {
        // Resolver URL relativa usando la URL base
        const absoluteUrl = new URL(href, baseUrl).href;
        const normalized = this.normalizeUrl(absoluteUrl);

        // Solo incluir enlaces del mismo origen (dominio)
        if (normalized.startsWith(baseOrigin)) {
          links.push(normalized);
        }
      } catch {
        // URL malformada — ignorar silenciosamente
      }
    }

    return links;
  }

  /**
   * Normalizar una URL para comparaciones consistentes.
   *
   * La normalización es crucial para el visited set: sin ella,
   * "https://ejemplo.com/about" y "https://ejemplo.com/about/"
   * se considerarían URLs diferentes, y visitaríamos la misma
   * página dos veces.
   *
   * Reglas de normalización:
   * 1. Eliminar trailing slash (excepto para la raíz del dominio)
   * 2. Eliminar fragmentos (#sección)
   * 3. Convertir a minúsculas el protocolo y host
   * 4. Eliminar parámetros de tracking comunes (utm_*)
   *
   * @param {string} url - URL a normalizar
   * @returns {string} URL normalizada
   */
  normalizeUrl(url) {
    try {
      const parsed = new URL(url);

      // Eliminar fragmento (#...)
      parsed.hash = '';

      // Eliminar parámetros de tracking (utm_*)
      const params = parsed.searchParams;
      const keysToDelete = [];
      for (const key of params.keys()) {
        if (key.startsWith('utm_')) {
          keysToDelete.push(key);
        }
      }
      for (const key of keysToDelete) {
        params.delete(key);
      }

      let normalized = parsed.href;

      // Eliminar trailing slash (pero no si es solo el origen + /)
      // "https://ejemplo.com/" se queda como está
      // "https://ejemplo.com/about/" se convierte en "https://ejemplo.com/about"
      if (parsed.pathname !== '/' && normalized.endsWith('/')) {
        normalized = normalized.slice(0, -1);
      }

      return normalized;
    } catch {
      return url;
    }
  }

  /** Obtener el site map construido durante el crawl */
  getSiteMap() {
    return this._siteMap;
  }

  /** Obtener el visited set (para debugging/testing) */
  getVisitedSet() {
    return this._visitedSet;
  }

  /** Obtener el número de páginas visitadas */
  get pagesVisited() {
    return this._pagesVisited;
  }

  /** Obtener errores encontrados durante el crawl */
  get errors() {
    return this._errors;
  }

  /** Obtener el semáforo interno (para testing) */
  get semaphore() {
    return this._semaphore;
  }
}

// =============================================================================
// Demo: Ejecutar el crawler con el MockWeb
// =============================================================================

async function runDemo() {
  console.log('='.repeat(60));
  console.log('🕷️  El Rastreador Cortés — Demo con MockWeb');
  console.log('='.repeat(60));
  console.log();

  const mockWeb = new MockWeb();

  const crawler = new WebCrawler({
    maxConcurrent: 2,
    maxPages: 20,
    delayMs: 10, // Rápido para la demo
    fetchFn: (url) => mockWeb.fetch(url),
  });

  console.log('🚀 Iniciando crawl desde https://ejemplo.com/ ...');
  console.log();

  const siteMap = await crawler.crawl('https://ejemplo.com/');

  console.log(`✅ Crawl completado. Páginas visitadas: ${crawler.pagesVisited}`);
  console.log();

  console.log('🗺️  Site Map descubierto:');
  console.log('-'.repeat(60));

  for (const [url, data] of siteMap) {
    console.log(`  📄 ${url}`);
    console.log(`     Título: ${data.title}`);
    if (data.links.length > 0) {
      console.log(`     Enlaces: ${data.links.join(', ')}`);
    } else {
      console.log('     Enlaces: (ninguno — dead end)');
    }
    console.log();
  }

  console.log('-'.repeat(60));
  console.log(`📊 Estadísticas:`);
  console.log(`   Total de páginas en el mapa: ${siteMap.size}`);
  console.log(`   Total de fetches realizados: ${mockWeb.getTotalFetchCount()}`);
  console.log(`   Errores: ${crawler.errors.length}`);

  if (crawler.errors.length > 0) {
    console.log('   Detalle de errores:');
    for (const err of crawler.errors) {
      console.log(`     ❌ ${err.url}: ${err.error}`);
    }
  }
}

// Ejecutar la demo solo si este archivo se ejecuta directamente
if (require.main === module) {
  runDemo().catch(console.error);
}

// =============================================================================
// Exportaciones
// =============================================================================

module.exports = { Semaphore, MockWeb, WebCrawler };
