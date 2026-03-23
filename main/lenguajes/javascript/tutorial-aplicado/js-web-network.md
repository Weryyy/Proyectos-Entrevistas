# 🌐 JavaScript Aplicado: Rastreo y Redes (Web Crawler)

Este tutorial muestra cómo JavaScript se convierte en un gigante de la red gracias a su arquitectura no bloqueante, basándose en el **Módulo 3 (Web Crawler)**.

---

## 🏗️ JS for Network Web Crawling

### 1. El Bucle de Eventos (Event Loop)
Gracias a `async/await`, el Módulo 3 no se detiene si una web tarda en cargar. Puede hacer cientos de peticiones simultáneas sin consumir gigabytes de RAM.

```javascript
// Descarga asíncrona de una página
const response = await fetch(url);
const html = await response.text();
```

### 2. Análisis del DOM con `cheerio`
JavaScript es el lenguaje nativo del navegador, por lo que analizar el árbol de una web es trivial con librerías que simulan la estructura de las webs reales.

---

## 🚀 Ampliación y Escalabilidad (Tecnología de última hora)

### Mejoras Modernas (2025-2026):
1. **Bun**: En lugar de Node.js, usar el runtime **Bun** para que el Módulo 3 corra un 300% más rápido gracias a su optimización con el motor de JavaScript Core de Apple.
2. **Playwright con Steal-JS**: No solo descargar HTML, sino renderizar webs con JavaScript pesado usando navegadores reales "sin cabeza" (Headless Browsers) para evitar bloqueos por parte de servidores.

### Cambios para Escalabilidad:
- **Proxies Rotativos**: Implementar rotación automática de IPs para que los servidores no baneen al crawler del Módulo 3.
- **Worker Threads**: Usar hilos paralelos de la CPU para procesar el HTML descargado mientras el hilo principal sigue capturando URLs.
