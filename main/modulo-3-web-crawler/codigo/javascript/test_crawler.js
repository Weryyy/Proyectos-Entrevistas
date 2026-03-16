// =============================================================================
// Tests del Módulo 3: El Rastreador Cortés — Web Crawler
// =============================================================================
// Suite de tests usando el test runner built-in de Node.js (node:test).
// Ejecutar con: node --test test_crawler.js
// =============================================================================

'use strict';

const { describe, test } = require('node:test');
const assert = require('node:assert/strict');
const { Semaphore, MockWeb, WebCrawler } = require('./crawler.js');

// =============================================================================
// Tests del Semáforo
// =============================================================================

describe('Semaphore — Control de concurrencia', () => {
  // Verificar que el semáforo limita correctamente el número de tareas
  // concurrentes. Esto es fundamental para la "cortesía" del crawler.
  test('Semaphore limits concurrency', async () => {
    const semaphore = new Semaphore(2); // Máximo 2 concurrentes
    let currentConcurrent = 0;
    let maxObservedConcurrent = 0;

    const task = async (id) => {
      await semaphore.acquire();
      currentConcurrent++;
      // Registrar el máximo de concurrencia observado
      if (currentConcurrent > maxObservedConcurrent) {
        maxObservedConcurrent = currentConcurrent;
      }
      // Simular trabajo asíncrono
      await new Promise((resolve) => setTimeout(resolve, 50));
      currentConcurrent--;
      semaphore.release();
    };

    // Lanzar 5 tareas simultáneas — solo 2 deberían estar activas a la vez
    await Promise.all([task(1), task(2), task(3), task(4), task(5)]);

    // El máximo de concurrencia observado no debe exceder el límite del semáforo
    assert.ok(
      maxObservedConcurrent <= 2,
      `La concurrencia máxima observada (${maxObservedConcurrent}) excede el límite (2)`
    );
    // Debe haber alcanzado el máximo permitido al menos una vez
    assert.equal(maxObservedConcurrent, 2, 'El semáforo debería permitir hasta 2 concurrentes');
  });

  test('Semaphore acquire/release cycle works correctly', async () => {
    const sem = new Semaphore(1);
    assert.equal(sem.availablePermits, 1, 'Debe iniciar con 1 permiso');

    await sem.acquire();
    assert.equal(sem.availablePermits, 0, 'Después de acquire, 0 permisos');

    sem.release();
    assert.equal(sem.availablePermits, 1, 'Después de release, 1 permiso');
  });

  test('Semaphore queues waiters when no permits available', async () => {
    const sem = new Semaphore(1);
    await sem.acquire(); // Toma el único permiso

    let secondAcquired = false;
    const waitPromise = sem.acquire().then(() => { secondAcquired = true; });

    // El segundo acquire debería estar esperando
    assert.equal(sem.waitingCount, 1, 'Debería haber 1 waiter en cola');
    assert.equal(secondAcquired, false, 'No debería haberse adquirido aún');

    // Liberar el permiso — el waiter debería despertar
    sem.release();
    await waitPromise;
    assert.equal(secondAcquired, true, 'Ahora debería haberse adquirido');
  });
});

// =============================================================================
// Tests del MockWeb
// =============================================================================

describe('MockWeb — Simulación del sitio web', () => {
  test('MockWeb returns pages correctly', async () => {
    const web = new MockWeb();
    const response = await web.fetch('https://ejemplo.com/');
    assert.equal(response.status, 200, 'La página raíz debe existir');
    assert.ok(response.body.includes('<title>'), 'Debe contener un título');
  });

  test('MockWeb returns 404 for unknown pages', async () => {
    const web = new MockWeb();
    const response = await web.fetch('https://ejemplo.com/no-existe');
    assert.equal(response.status, 404, 'Debe retornar 404 para páginas inexistentes');
  });

  test('MockWeb tracks fetch count', async () => {
    const web = new MockWeb();
    await web.fetch('https://ejemplo.com/');
    await web.fetch('https://ejemplo.com/');
    assert.equal(web.getFetchCount('https://ejemplo.com/'), 2, 'Debe contar 2 fetches');
  });
});

// =============================================================================
// Tests del WebCrawler — BFS y Visited Set
// =============================================================================

describe('WebCrawler — BFS traversal', () => {
  // El test más importante: verificar que BFS visita TODAS las páginas
  // alcanzables desde la URL semilla, sin dejarse ninguna.
  test('BFS traversal visits all reachable pages', async () => {
    const mockWeb = new MockWeb();
    const crawler = new WebCrawler({
      maxConcurrent: 3,
      maxPages: 50,
      delayMs: 0, // Sin delay para tests rápidos
      fetchFn: (url) => mockWeb.fetch(url),
    });

    await crawler.crawl('https://ejemplo.com/');
    const siteMap = crawler.getSiteMap();

    // El MockWeb tiene 8 páginas — todas deben estar en el site map
    const expectedUrls = [
      'https://ejemplo.com/',
      'https://ejemplo.com/about',
      'https://ejemplo.com/blog',
      'https://ejemplo.com/blog/post-1',
      'https://ejemplo.com/blog/post-2',
      'https://ejemplo.com/team',
      'https://ejemplo.com/contact',
      'https://ejemplo.com/dead-end',
    ];

    for (const url of expectedUrls) {
      assert.ok(siteMap.has(url), `El site map debe contener: ${url}`);
    }

    assert.equal(siteMap.size, expectedUrls.length, 'Debe tener exactamente 8 páginas');
  });

  // El visited set debe evitar que una página se visite (fetch) más de una vez.
  // Esto es lo que previene los ciclos infinitos y el trabajo duplicado.
  test('Visited set prevents duplicate visits', async () => {
    const mockWeb = new MockWeb();
    const crawler = new WebCrawler({
      maxConcurrent: 2,
      maxPages: 50,
      delayMs: 0,
      fetchFn: (url) => mockWeb.fetch(url),
    });

    await crawler.crawl('https://ejemplo.com/');

    // Verificar que cada URL fue fetcheada exactamente una vez
    // (el visited set debe prevenir duplicados)
    const visitedUrls = crawler.getVisitedSet();
    for (const url of visitedUrls) {
      const fetchCount = mockWeb.getFetchCount(url);
      assert.equal(
        fetchCount, 1,
        `La URL ${url} fue fetcheada ${fetchCount} veces (esperado: 1)`
      );
    }
  });

  // El grafo del MockWeb tiene ciclos:
  // team → inicio (ciclo) y post-2 → post-1 (ciclo)
  // El crawler debe manejarlos sin entrar en un loop infinito.
  test('Handles circular links without infinite loop', async () => {
    // Crear un grafo pequeño con un ciclo directo: A → B → A
    const mockWeb = new MockWeb();
    mockWeb.setPage('https://ciclo.com/', `
      <html><head><title>A</title></head><body>
        <a href="https://ciclo.com/b">Ir a B</a>
      </body></html>
    `);
    mockWeb.setPage('https://ciclo.com/b', `
      <html><head><title>B</title></head><body>
        <a href="https://ciclo.com/">Volver a A</a>
      </body></html>
    `);

    const crawler = new WebCrawler({
      maxConcurrent: 1,
      maxPages: 100,
      delayMs: 0,
      fetchFn: (url) => mockWeb.fetch(url),
    });

    // Si hay un bug en el visited set, esto se colgaría
    await crawler.crawl('https://ciclo.com/');
    const siteMap = crawler.getSiteMap();

    assert.equal(siteMap.size, 2, 'Solo debe haber 2 páginas en el ciclo');
    assert.ok(siteMap.has('https://ciclo.com/'), 'Debe contener A');
    assert.ok(siteMap.has('https://ciclo.com/b'), 'Debe contener B');

    // Verificar que cada página se visitó exactamente una vez
    assert.equal(mockWeb.getFetchCount('https://ciclo.com/'), 1);
    assert.equal(mockWeb.getFetchCount('https://ciclo.com/b'), 1);
  });

  // El crawler debe respetar el límite de páginas máximas,
  // deteniéndose incluso si hay más páginas por descubrir.
  test('Respects maxPages limit', async () => {
    const mockWeb = new MockWeb();
    const crawler = new WebCrawler({
      maxConcurrent: 1,
      maxPages: 3, // Solo 3 páginas de las 8 disponibles
      delayMs: 0,
      fetchFn: (url) => mockWeb.fetch(url),
    });

    await crawler.crawl('https://ejemplo.com/');
    const siteMap = crawler.getSiteMap();

    assert.equal(siteMap.size, 3, 'Debe detenerse después de 3 páginas');
    assert.equal(crawler.pagesVisited, 3, 'El contador debe ser 3');
  });

  // Las páginas sin enlaces (dead-ends) no deben causar errores,
  // simplemente se agregan al site map con una lista de enlaces vacía.
  test('Handles dead-end pages gracefully', async () => {
    const mockWeb = new MockWeb();
    // Crear un sitio donde la página raíz enlaza a un dead-end directo
    mockWeb.setPage('https://dead.com/', `
      <html><head><title>Inicio</title></head><body>
        <a href="https://dead.com/fin">Fin</a>
      </body></html>
    `);
    mockWeb.setPage('https://dead.com/fin', `
      <html><head><title>Fin</title></head><body>
        <p>No hay más enlaces.</p>
      </body></html>
    `);

    const crawler = new WebCrawler({
      maxConcurrent: 1,
      maxPages: 10,
      delayMs: 0,
      fetchFn: (url) => mockWeb.fetch(url),
    });

    await crawler.crawl('https://dead.com/');
    const siteMap = crawler.getSiteMap();

    assert.equal(siteMap.size, 2, 'Debe tener 2 páginas');
    assert.ok(siteMap.has('https://dead.com/fin'), 'Debe incluir el dead-end');
    assert.deepEqual(
      siteMap.get('https://dead.com/fin').links, [],
      'El dead-end no debe tener enlaces'
    );
  });
});

// =============================================================================
// Tests de normalización de URLs
// =============================================================================

describe('WebCrawler — URL normalization', () => {
  test('URL normalization works correctly', () => {
    const crawler = new WebCrawler();

    // Eliminar trailing slash
    assert.equal(
      crawler.normalizeUrl('https://ejemplo.com/about/'),
      'https://ejemplo.com/about',
      'Debe eliminar trailing slash'
    );

    // Mantener trailing slash en la raíz
    assert.equal(
      crawler.normalizeUrl('https://ejemplo.com/'),
      'https://ejemplo.com/',
      'Debe mantener trailing slash en la raíz'
    );

    // Eliminar fragmento (#)
    assert.equal(
      crawler.normalizeUrl('https://ejemplo.com/page#section'),
      'https://ejemplo.com/page',
      'Debe eliminar el fragmento'
    );

    // Eliminar parámetros UTM
    assert.equal(
      crawler.normalizeUrl('https://ejemplo.com/page?utm_source=test&id=1'),
      'https://ejemplo.com/page?id=1',
      'Debe eliminar parámetros utm_*'
    );

    // Combinar múltiples normalizaciones
    assert.equal(
      crawler.normalizeUrl('https://ejemplo.com/about/#top?utm_campaign=x'),
      'https://ejemplo.com/about',
      'Debe aplicar todas las normalizaciones'
    );
  });

  test('normalizeUrl handles edge cases', () => {
    const crawler = new WebCrawler();

    // URL inválida — devolver tal cual
    assert.equal(
      crawler.normalizeUrl('not-a-url'),
      'not-a-url',
      'Debe devolver URLs inválidas sin cambios'
    );

    // URL con query string sin UTM
    assert.equal(
      crawler.normalizeUrl('https://ejemplo.com/search?q=test'),
      'https://ejemplo.com/search?q=test',
      'Debe mantener query strings normales'
    );
  });
});

// =============================================================================
// Tests del Site Map
// =============================================================================

describe('WebCrawler — Site Map', () => {
  // Verificar que el site map refleja correctamente la estructura del grafo.
  // Cada entrada debe tener el título de la página y sus enlaces salientes.
  test('Generates correct site map', async () => {
    const mockWeb = new MockWeb();
    const crawler = new WebCrawler({
      maxConcurrent: 2,
      maxPages: 50,
      delayMs: 0,
      fetchFn: (url) => mockWeb.fetch(url),
    });

    await crawler.crawl('https://ejemplo.com/');
    const siteMap = crawler.getSiteMap();

    // Verificar la página de inicio
    const homePage = siteMap.get('https://ejemplo.com/');
    assert.ok(homePage, 'La página de inicio debe existir en el site map');
    assert.equal(homePage.title, 'Inicio - Ejemplo', 'El título debe coincidir');
    assert.ok(
      homePage.links.includes('https://ejemplo.com/about'),
      'Debe incluir enlace a /about'
    );
    assert.ok(
      homePage.links.includes('https://ejemplo.com/blog'),
      'Debe incluir enlace a /blog'
    );

    // Verificar una página con ciclo (team enlaza de vuelta al inicio)
    const teamPage = siteMap.get('https://ejemplo.com/team');
    assert.ok(teamPage, 'La página de team debe existir');
    assert.ok(
      teamPage.links.includes('https://ejemplo.com/'),
      'Team debe enlazar de vuelta al inicio'
    );

    // Verificar dead-end (sin enlaces)
    const deadEnd = siteMap.get('https://ejemplo.com/dead-end');
    assert.ok(deadEnd, 'La página dead-end debe existir');
    assert.equal(deadEnd.title, 'Fin del Camino');
    assert.equal(deadEnd.links.length, 0, 'Dead-end no debe tener enlaces');

    // Verificar la página de contacto (sin enlaces <a>)
    const contactPage = siteMap.get('https://ejemplo.com/contact');
    assert.ok(contactPage, 'La página de contacto debe existir');
    assert.equal(contactPage.title, 'Contacto');
  });
});
