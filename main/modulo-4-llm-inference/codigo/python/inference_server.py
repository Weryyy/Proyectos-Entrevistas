"""
🔮 Módulo 4: Simulador de Inferencia de LLM — System Design
=============================================================

Este módulo simula los componentes internos de un servidor de inferencia
para modelos de lenguaje grandes (LLMs). No ejecuta un modelo real, sino
que replica la arquitectura y lógica de sistemas como vLLM, TGI (Text
Generation Inference) o TensorRT-LLM.

Conceptos clave simulados:
    1. **KV Cache** — Almacena estados intermedios de atención (Key/Value)
       para evitar recálculos costosos durante la generación autoregresiva.
    2. **Batch Scheduler** — Agrupa peticiones para maximizar el uso de GPU,
       intentando agrupar secuencias de longitud similar.
    3. **Streaming** — Devuelve tokens conforme se generan, reduciendo la
       latencia percibida por el usuario.
    4. **Token Generator** — Simula la generación de tokens (en un sistema
       real, aquí estaría el forward pass del transformer).

Arquitectura:
    ┌──────────────────────────────────────────────────┐
    │              InferenceServer                     │
    │                                                  │
    │  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
    │  │ Batch    │  │   KV Cache   │  │  Token    │  │
    │  │Scheduler │  │  (memoria    │  │ Generator │  │
    │  │(cola +   │  │   cristalina │  │ (oráculo) │  │
    │  │ batching)│  │   del        │  │           │  │
    │  │          │  │   oráculo)   │  │           │  │
    │  └──────────┘  └──────────────┘  └───────────┘  │
    └──────────────────────────────────────────────────┘

Ejecutar:
    python inference_server.py
"""

from __future__ import annotations

import random
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Generator


# ═══════════════════════════════════════════════════════════════════════
# 📦 Request — Representa una petición de inferencia
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class Request:
    """Representa una petición de inferencia al servidor.

    En un sistema real, cada petición llega con un prompt y parámetros
    de generación (max_tokens, temperature, top_p, etc.). El servidor
    le asigna un ID único y rastrea su progreso.

    Attributes:
        id: Identificador único de la petición.
        prompt: Texto de entrada del usuario.
        max_tokens: Número máximo de tokens a generar.
        arrival_time: Momento en que llegó la petición (epoch).
        tokens_generated: Número de tokens generados hasta ahora.
        status: Estado actual — "pending", "running", "completed".
        output_tokens: Lista de tokens generados hasta ahora.
    """

    id: str
    prompt: str
    max_tokens: int
    arrival_time: float
    tokens_generated: int = 0
    status: str = "pending"
    output_tokens: list[str] = field(default_factory=list)

    @property
    def prompt_length(self) -> int:
        """Longitud aproximada del prompt en 'tokens' (palabras)."""
        return len(self.prompt.split())

    @property
    def is_complete(self) -> bool:
        """Indica si la petición ha generado todos sus tokens."""
        return self.tokens_generated >= self.max_tokens


# ═══════════════════════════════════════════════════════════════════════
# 🧊 KVCache — Memoria cristalina del oráculo galáctico
# ═══════════════════════════════════════════════════════════════════════


class KVCache:
    """Simulador de KV Cache para inferencia de transformers.

    ¿Por qué es importante el KV Cache?
    ────────────────────────────────────
    En la generación autoregresiva, cada nuevo token necesita "atender"
    a todos los tokens anteriores. Sin caché, generar el token N requiere
    recalcular los estados de atención (Key y Value) de los N-1 tokens
    previos en CADA capa del transformer.

    Con el KV Cache, almacenamos estos estados intermedios y solo
    calculamos los del token nuevo. Esto convierte una operación O(n²)
    por secuencia completa en O(n).

    Estructura en memoria:
        cache[request_id][layer] = (key_states, value_states)

    En un sistema real:
        - Los key_states y value_states son tensores de dimensión
          [batch, num_heads, seq_len, head_dim].
        - La memoria crece linealmente con la longitud de la secuencia.
        - Para un modelo de 70B con 80 capas, el KV Cache de una sola
          secuencia de 4096 tokens puede ocupar ~2.5 GB.

    Attributes:
        max_memory_mb: Presupuesto máximo de memoria en megabytes.
        _cache: Diccionario anidado con los estados almacenados.
        _memory_used_mb: Memoria actualmente en uso.
    """

    def __init__(self, max_memory_mb: float) -> None:
        """Inicializa el KV Cache con un presupuesto de memoria.

        Args:
            max_memory_mb: Memoria máxima permitida en megabytes.
                           En producción, esto sería memoria GPU (VRAM).

        Raises:
            ValueError: Si el presupuesto de memoria es menor o igual a 0.
        """
        if max_memory_mb <= 0:
            raise ValueError("El presupuesto de memoria debe ser positivo")

        self.max_memory_mb = max_memory_mb
        # Estructura: {request_id: {layer: (key_states, value_states)}}
        self._cache: dict[str, dict[int, tuple[Any, Any]]] = {}
        self._memory_used_mb: float = 0.0

    def store(
        self,
        request_id: str,
        layer: int,
        key_states: Any,
        value_states: Any,
    ) -> bool:
        """Almacena estados de atención en el caché.

        En un transformer real, después de cada paso de atención en cada
        capa, se concatenan los nuevos K,V con los existentes en el caché.
        Aquí simulamos ese almacenamiento.

        Args:
            request_id: ID de la petición a la que pertenecen los estados.
            layer: Número de capa del transformer (0, 1, 2, ...).
            key_states: Estados Key de la capa de atención.
            value_states: Estados Value de la capa de atención.

        Returns:
            True si se almacenó correctamente, False si no hay memoria.
        """
        # Simulamos que cada entrada de caché ocupa un tamaño fijo.
        # En la realidad, el tamaño depende de: num_heads × head_dim × seq_len × 2 (K+V) × dtype_size
        entry_size_mb = 0.5  # Tamaño simulado por capa

        # Verificar si la entrada ya existía (actualización, no nuevo gasto)
        is_update = (
            request_id in self._cache and layer in self._cache[request_id]
        )

        if not is_update and self._memory_used_mb + entry_size_mb > self.max_memory_mb:
            # No hay espacio — en producción se aplicaría una política de evicción
            # (ej: evictar la petición más antigua o la de menor prioridad)
            return False

        if request_id not in self._cache:
            self._cache[request_id] = {}

        if not is_update:
            self._memory_used_mb += entry_size_mb

        self._cache[request_id][layer] = (key_states, value_states)
        return True

    def get(self, request_id: str, layer: int) -> tuple[Any, Any] | None:
        """Recupera estados de atención del caché.

        En cada paso de generación, el transformer necesita los K,V
        previos para calcular la atención. Esta operación debe ser O(1).

        Args:
            request_id: ID de la petición.
            layer: Número de capa.

        Returns:
            Tupla (key_states, value_states) si existe, None si no.
        """
        if request_id not in self._cache:
            return None
        return self._cache[request_id].get(layer)

    def evict(self, request_id: str) -> float:
        """Elimina todos los estados almacenados para una petición.

        Esto ocurre cuando una petición completa su generación o cuando
        se necesita liberar memoria para nuevas peticiones. Es crítico
        liberar el KV Cache inmediatamente — en un sistema real, esta
        memoria GPU es el recurso más escaso.

        Args:
            request_id: ID de la petición a evictar.

        Returns:
            Cantidad de memoria liberada en MB.
        """
        if request_id not in self._cache:
            return 0.0

        num_layers = len(self._cache[request_id])
        memory_freed = num_layers * 0.5  # 0.5 MB por capa (simulado)
        del self._cache[request_id]
        self._memory_used_mb = max(0.0, self._memory_used_mb - memory_freed)
        return memory_freed

    def get_memory_usage(self) -> dict[str, float]:
        """Devuelve estadísticas de uso de memoria del caché.

        Returns:
            Diccionario con memoria usada, total y porcentaje.
        """
        return {
            "used_mb": round(self._memory_used_mb, 2),
            "total_mb": self.max_memory_mb,
            "usage_percent": round(
                (self._memory_used_mb / self.max_memory_mb) * 100, 2
            ),
            "num_requests_cached": len(self._cache),
        }


# ═══════════════════════════════════════════════════════════════════════
# 🎲 TokenGenerator — El oráculo que genera palabras
# ═══════════════════════════════════════════════════════════════════════


class TokenGenerator:
    """Generador simulado de tokens.

    En un sistema real, aquí estaría el forward pass del transformer:
        1. Embedding del token de entrada.
        2. Paso por N capas de atención (usando el KV Cache).
        3. Capa de proyección final (lm_head).
        4. Sampling (temperature, top-p, top-k) sobre el vocabulario.

    Nosotros simulamos este proceso devolviendo palabras aleatorias
    de un vocabulario predefinido, con un pequeño delay para simular
    el tiempo de cómputo real.

    Attributes:
        vocabulary: Lista de palabras que el "modelo" puede generar.
    """

    def __init__(self) -> None:
        """Inicializa el generador con un vocabulario simulado."""
        # Vocabulario temático: respuestas del oráculo galáctico 🌌
        self.vocabulary: list[str] = [
            "el", "la", "los", "las", "un", "una",
            "cosmos", "estrella", "galaxia", "nebulosa", "planeta",
            "quantum", "energía", "materia", "tiempo", "espacio",
            "sabiduría", "conocimiento", "verdad", "respuesta",
            "luz", "oscuridad", "infinito", "dimensión", "universo",
            "es", "será", "fue", "existe", "fluye",
            "entre", "sobre", "bajo", "dentro", "más allá",
            "del", "al", "con", "sin", "por",
            "antiguo", "eterno", "brillante", "profundo", "vasto",
        ]

    def generate_token(self, prompt_tokens: list[str] | None = None) -> str:
        """Genera un token simulado.

        En un transformer real, la distribución de probabilidad del
        siguiente token depende de TODOS los tokens anteriores (gracias
        al mecanismo de atención). Aquí simplificamos con selección
        aleatoria, pero mantenemos la interfaz correcta.

        Args:
            prompt_tokens: Tokens anteriores (contexto). En un sistema
                          real, estos influirían en la predicción.
                          Se mantiene en la firma para reflejar la API
                          real de un modelo autoregresivo.

        Returns:
            Un token (palabra) del vocabulario.
        """
        # En un modelo real, prompt_tokens alimentaría el mecanismo de
        # atención para condicionar la distribución del siguiente token.
        _ = prompt_tokens
        return random.choice(self.vocabulary)


# ═══════════════════════════════════════════════════════════════════════
# 📋 BatchScheduler — El estratega que organiza las consultas
# ═══════════════════════════════════════════════════════════════════════


class BatchScheduler:
    """Planificador de batches para inferencia eficiente.

    ¿Por qué agrupar peticiones en batches?
    ────────────────────────────────────────
    Las GPUs son procesadores masivamente paralelos. Procesar una sola
    secuencia usa una fracción mínima de su capacidad. Agrupar múltiples
    secuencias en un batch permite saturar la GPU y aumentar el throughput.

    Batching estático vs. continuo:
    ──────────────────────────────
    - **Estático:** Se forma un batch, se procesan TODAS las peticiones
      hasta que la más larga termine. Las cortas desperdician ciclos
      esperando. Ejemplo: si el batch tiene peticiones de 10 y 100 tokens,
      la de 10 tokens "espera" 90 pasos sin hacer nada útil.

    - **Continuo (iteration-level):** En cada paso de inferencia, las
      peticiones completadas se retiran y nuevas peticiones pueden entrar.
      Esto maximiza la utilización de la GPU.

    Este simulador implementa un esquema **continuo**: en cada `step()`
    del servidor, se pueden incorporar nuevas peticiones al batch.

    Optimización por longitud similar:
    ──────────────────────────────────
    Agrupamos peticiones con longitudes de prompt similares. ¿Por qué?
    Porque en un batch, todas las secuencias se rellenan (padding) hasta
    la longitud de la más larga. Si mezclamos una de 10 tokens con una
    de 500, la de 10 desperdicia 490 posiciones de cómputo.

    Attributes:
        max_batch_size: Número máximo de peticiones en un batch.
        max_token_budget: Presupuesto máximo de tokens totales por batch.
        _pending_queue: Cola de peticiones esperando ser procesadas.
    """

    def __init__(self, max_batch_size: int, max_token_budget: int) -> None:
        """Configura el planificador de batches.

        Args:
            max_batch_size: Máximo de peticiones simultáneas en un batch.
            max_token_budget: Máximo de tokens totales que el batch puede
                             manejar (prompt + generación). Esto refleja
                             la limitación de memoria de la GPU.

        Raises:
            ValueError: Si los parámetros son inválidos.
        """
        if max_batch_size < 1:
            raise ValueError("El tamaño máximo de batch debe ser al menos 1")
        if max_token_budget < 1:
            raise ValueError("El presupuesto de tokens debe ser al menos 1")

        self.max_batch_size = max_batch_size
        self.max_token_budget = max_token_budget
        self._pending_queue: list[Request] = []

    def add_request(self, request: Request) -> None:
        """Añade una petición a la cola de espera.

        Las peticiones se encolan por orden de llegada (FIFO) y se
        procesarán cuando el scheduler forme el siguiente batch.

        Args:
            request: Petición de inferencia a encolar.
        """
        self._pending_queue.append(request)

    def form_batch(self) -> list[Request]:
        """Forma un batch de peticiones para la siguiente iteración.

        Algoritmo de formación de batch:
            1. Ordena las peticiones pendientes por longitud de prompt.
               Esto agrupa secuencias similares, minimizando el padding
               desperdiciado.
            2. Selecciona peticiones hasta llenar el batch o agotar el
               presupuesto de tokens.
            3. Las peticiones seleccionadas se marcan como "running".

        En sistemas de producción (como vLLM), el scheduling es más
        sofisticado: se usa PagedAttention para manejar memoria de forma
        dinámica, y el scheduler considera la prioridad de las peticiones,
        sus SLAs (Service Level Agreements), etc.

        Returns:
            Lista de peticiones que forman el batch actual.
        """
        if not self._pending_queue:
            return []

        # Ordenar por longitud de prompt para agrupar similares
        # Esto reduce el padding y mejora la eficiencia de la GPU
        self._pending_queue.sort(key=lambda r: r.prompt_length)

        batch: list[Request] = []
        total_tokens = 0
        remaining: list[Request] = []

        for request in self._pending_queue:
            estimated_tokens = request.prompt_length + request.max_tokens
            can_fit_in_batch = len(batch) < self.max_batch_size
            can_fit_in_budget = total_tokens + estimated_tokens <= self.max_token_budget

            if can_fit_in_batch and can_fit_in_budget:
                request.status = "running"
                batch.append(request)
                total_tokens += estimated_tokens
            else:
                remaining.append(request)

        self._pending_queue = remaining
        return batch

    @property
    def pending_count(self) -> int:
        """Número de peticiones en espera."""
        return len(self._pending_queue)


# ═══════════════════════════════════════════════════════════════════════
# 🔮 InferenceServer — El corazón del oráculo galáctico
# ═══════════════════════════════════════════════════════════════════════


class InferenceServer:
    """Servidor simulado de inferencia de LLM.

    Este servidor orquesta todos los componentes:
        1. Recibe peticiones de los usuarios.
        2. El BatchScheduler las agrupa en batches eficientes.
        3. En cada paso (step), genera un token por petición en el batch.
        4. El KV Cache almacena los estados intermedios.
        5. Las respuestas se pueden consumir vía streaming.

    Flujo de una petición:
        submit_request() → cola pendiente → form_batch() → step() →
        → generar token → actualizar KV Cache → ¿completada? →
        → sí: evictar KV Cache y marcar como completada
        → no: continuar en el siguiente step()

    Attributes:
        model_name: Nombre del modelo simulado.
        scheduler: Planificador de batches.
        kv_cache: Caché de estados de atención.
        token_generator: Generador simulado de tokens.
        _requests: Registro de todas las peticiones.
        _active_batch: Batch actualmente en procesamiento.
        _total_tokens_generated: Contador total de tokens generados.
        _total_steps: Número total de pasos de inferencia ejecutados.
    """

    NUM_LAYERS = 4  # Número simulado de capas del transformer

    def __init__(
        self,
        model_name: str = "oraculo-galactico-7B",
        max_batch_size: int = 8,
        kv_cache_size_mb: float = 100.0,
    ) -> None:
        """Inicializa el servidor de inferencia.

        Args:
            model_name: Nombre identificador del modelo.
            max_batch_size: Máximo de peticiones por batch.
            kv_cache_size_mb: Memoria asignada al KV Cache en MB.
        """
        self.model_name = model_name
        self.scheduler = BatchScheduler(
            max_batch_size=max_batch_size,
            max_token_budget=max_batch_size * 512,
        )
        self.kv_cache = KVCache(max_memory_mb=kv_cache_size_mb)
        self.token_generator = TokenGenerator()

        self._requests: dict[str, Request] = {}
        self._active_batch: list[Request] = []
        self._total_tokens_generated: int = 0
        self._total_steps: int = 0

    def submit_request(self, prompt: str, max_tokens: int = 10) -> str:
        """Envía una nueva petición de inferencia al servidor.

        Args:
            prompt: Texto de entrada del usuario.
            max_tokens: Número máximo de tokens a generar.

        Returns:
            ID único de la petición para rastreo y streaming.

        Raises:
            ValueError: Si el prompt está vacío o max_tokens < 1.
        """
        if not prompt or not prompt.strip():
            raise ValueError("El prompt no puede estar vacío")
        if max_tokens < 1:
            raise ValueError("max_tokens debe ser al menos 1")

        request_id = str(uuid.uuid4())[:8]
        request = Request(
            id=request_id,
            prompt=prompt,
            max_tokens=max_tokens,
            arrival_time=time.time(),
        )

        self._requests[request_id] = request
        self.scheduler.add_request(request)
        return request_id

    def step(self) -> dict[str, Any]:
        """Ejecuta un paso de inferencia.

        Este es el bucle principal del servidor. En cada paso:
            1. Si no hay batch activo, forma uno nuevo con el scheduler.
            2. Para cada petición en el batch, genera un token.
            3. Actualiza el KV Cache con los nuevos estados.
            4. Verifica qué peticiones han completado su generación.
            5. Retira las peticiones completadas y libera su KV Cache.

        En un sistema real, este paso corresponde a una iteración del
        bucle de inferencia: un forward pass del modelo para todo el batch.

        Returns:
            Diccionario con estadísticas del paso:
                - tokens_generated: tokens generados en este paso.
                - completed: lista de IDs de peticiones completadas.
                - batch_size: tamaño del batch actual.
                - pending: peticiones aún en cola.
        """
        # Si no hay batch activo o el anterior se completó, formar uno nuevo
        # Esto implementa batching continuo: en cada paso podemos incorporar
        # nuevas peticiones al batch
        self._active_batch = [r for r in self._active_batch if not r.is_complete]

        # Intentar incorporar nuevas peticiones al batch existente
        new_requests = self.scheduler.form_batch()
        self._active_batch.extend(new_requests)

        if not self._active_batch:
            return {
                "tokens_generated": 0,
                "completed": [],
                "batch_size": 0,
                "pending": self.scheduler.pending_count,
            }

        self._total_steps += 1
        tokens_this_step = 0
        completed_ids: list[str] = []

        # Generar un token para cada petición en el batch
        # En la GPU real, esto sería un solo forward pass paralelo
        for request in self._active_batch:
            if request.is_complete:
                continue

            # Generar el siguiente token
            token = self.token_generator.generate_token(request.output_tokens)
            request.output_tokens.append(token)
            request.tokens_generated += 1
            tokens_this_step += 1
            self._total_tokens_generated += 1

            # Actualizar el KV Cache — en cada capa del transformer,
            # almacenamos los nuevos estados K,V para este token
            for layer_idx in range(self.NUM_LAYERS):
                # Simulamos los estados como listas de floats
                key_state = [random.random() for _ in range(4)]
                value_state = [random.random() for _ in range(4)]
                self.kv_cache.store(request.id, layer_idx, key_state, value_state)

            # Verificar si la petición se completó
            if request.is_complete:
                request.status = "completed"
                completed_ids.append(request.id)
                # Liberar el KV Cache — ¡memoria GPU liberada!
                self.kv_cache.evict(request.id)

        return {
            "tokens_generated": tokens_this_step,
            "completed": completed_ids,
            "batch_size": len(self._active_batch),
            "pending": self.scheduler.pending_count,
        }

    def stream_response(self, request_id: str) -> Generator[str, None, None]:
        """Genera tokens de respuesta conforme se producen (streaming).

        Este generador permite al cliente recibir tokens uno a uno en vez
        de esperar a que la respuesta completa esté lista. En producción,
        esto se implementaría con Server-Sent Events (SSE) o WebSockets.

        Args:
            request_id: ID de la petición a transmitir.

        Yields:
            Cada token generado, uno a la vez.

        Raises:
            KeyError: Si el request_id no existe.
        """
        if request_id not in self._requests:
            raise KeyError(f"Petición '{request_id}' no encontrada")

        request = self._requests[request_id]
        tokens_yielded = 0

        # Entregamos tokens conforme se van generando
        # En un sistema real, esto bloquearía hasta que haya un nuevo token
        while not request.is_complete or tokens_yielded < request.tokens_generated:
            if tokens_yielded < request.tokens_generated:
                yield request.output_tokens[tokens_yielded]
                tokens_yielded += 1
            else:
                # No hay tokens nuevos aún — en producción esperaríamos
                # con un mecanismo asíncrono (asyncio.Event, etc.)
                break

    def get_stats(self) -> dict[str, Any]:
        """Devuelve estadísticas del servidor.

        Returns:
            Diccionario con métricas del servidor:
                - model_name: nombre del modelo.
                - total_requests: peticiones recibidas.
                - pending_requests: peticiones en cola.
                - active_batch_size: tamaño del batch actual.
                - completed_requests: peticiones completadas.
                - total_tokens_generated: total de tokens generados.
                - total_steps: pasos de inferencia ejecutados.
                - kv_cache_usage: estadísticas del KV Cache.
                - throughput_tokens_per_step: tokens promedio por paso.
        """
        completed = sum(
            1 for r in self._requests.values() if r.status == "completed"
        )
        throughput = (
            self._total_tokens_generated / self._total_steps
            if self._total_steps > 0
            else 0.0
        )

        return {
            "model_name": self.model_name,
            "total_requests": len(self._requests),
            "pending_requests": self.scheduler.pending_count,
            "active_batch_size": len(self._active_batch),
            "completed_requests": completed,
            "total_tokens_generated": self._total_tokens_generated,
            "total_steps": self._total_steps,
            "kv_cache_usage": self.kv_cache.get_memory_usage(),
            "throughput_tokens_per_step": round(throughput, 2),
        }

    def get_request(self, request_id: str) -> Request | None:
        """Obtiene una petición por su ID.

        Args:
            request_id: ID de la petición.

        Returns:
            La petición si existe, None si no.
        """
        return self._requests.get(request_id)


# ═══════════════════════════════════════════════════════════════════════
# 🚀 Demostración interactiva
# ═══════════════════════════════════════════════════════════════════════


def _run_demo() -> None:
    """Ejecuta la demostración interactiva del servidor de inferencia."""
    print("=" * 65)
    print("  🔮 Oráculo Galáctico — Servidor de Inferencia de LLM")
    print("=" * 65)
    print()

    # ── Crear el servidor ──
    server = InferenceServer(
        model_name="oraculo-galactico-7B",
        max_batch_size=4,
        kv_cache_size_mb=50.0,
    )
    print(f"📡 Servidor inicializado: {server.model_name}")
    print(f"   Max batch size: {server.scheduler.max_batch_size}")
    print(f"   KV Cache: {server.kv_cache.max_memory_mb} MB")
    print()

    # ── Enviar peticiones simuladas ──
    print("─" * 65)
    print("  📨 Enviando consultas al oráculo...")
    print("─" * 65)
    prompts = [
        ("¿Cuál es el sentido del cosmos?", 5),
        ("Explica la naturaleza del tiempo", 8),
        ("¿Qué hay más allá del universo observable?", 3),
        ("Describe la energía oscura en términos simples", 6),
        ("¿Existe vida en otras galaxias?", 4),
        ("¿Cómo nacen las estrellas?", 7),
    ]

    request_ids: list[str] = []
    for prompt, max_tokens in prompts:
        rid = server.submit_request(prompt, max_tokens)
        request_ids.append(rid)
        print(f"   ✉️  [{rid}] \"{prompt}\" (max_tokens={max_tokens})")

    print()
    print(f"   📊 Peticiones en cola: {server.scheduler.pending_count}")
    print()

    # ── Ejecutar pasos de inferencia ──
    print("─" * 65)
    print("  ⚡ Ejecutando pasos de inferencia...")
    print("─" * 65)

    max_steps = 20
    for step_num in range(1, max_steps + 1):
        result = server.step()

        if result["batch_size"] == 0 and result["pending"] == 0:
            print(f"\n   ✅ Todas las peticiones completadas en {step_num - 1} pasos.")
            break

        completed_info = ""
        if result["completed"]:
            completed_info = f" | Completadas: {result['completed']}"

        print(
            f"   Paso {step_num:2d}: "
            f"batch={result['batch_size']} "
            f"tokens={result['tokens_generated']} "
            f"pendientes={result['pending']}"
            f"{completed_info}"
        )
    print()

    # ── Mostrar respuestas con streaming simulado ──
    print("─" * 65)
    print("  🌟 Respuestas del oráculo (streaming)...")
    print("─" * 65)

    for rid in request_ids:
        request = server.get_request(rid)
        if request is None:
            continue
        tokens = list(server.stream_response(rid))
        response_text = " ".join(tokens)
        print(f"\n   🔮 [{rid}] \"{request.prompt}\"")
        print(f"      → {response_text}")
        print(f"      ({request.tokens_generated} tokens, estado: {request.status})")

    print()

    # ── Estadísticas finales ──
    print("─" * 65)
    print("  📊 Estadísticas del servidor")
    print("─" * 65)
    stats = server.get_stats()
    print(f"   Modelo:                {stats['model_name']}")
    print(f"   Total peticiones:      {stats['total_requests']}")
    print(f"   Completadas:           {stats['completed_requests']}")
    print(f"   Total tokens:          {stats['total_tokens_generated']}")
    print(f"   Pasos de inferencia:   {stats['total_steps']}")
    print(f"   Throughput:            {stats['throughput_tokens_per_step']} tokens/paso")

    cache_usage = stats["kv_cache_usage"]
    print(f"   KV Cache usado:        {cache_usage['used_mb']} / {cache_usage['total_mb']} MB")
    print(f"   KV Cache %:            {cache_usage['usage_percent']}%")
    print(f"   Requests en caché:     {cache_usage['num_requests_cached']}")
    print()
    print("=" * 65)
    print("  🌌 El oráculo ha respondido. Que el cosmos te guíe.")
    print("=" * 65)


if __name__ == "__main__":
    # Semilla fija para reproducibilidad en la demostración
    random.seed(42)
    _run_demo()
    sys.exit(0)
