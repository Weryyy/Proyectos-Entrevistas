"""
Suite de pruebas para el Simulador de Inferencia de LLM — Módulo 4.

Ejecutar con: pytest test_inference_server.py -v
"""

from __future__ import annotations

import time

import pytest

from inference_server import (
    BatchScheduler,
    InferenceServer,
    KVCache,
    Request,
    TokenGenerator,
)


# ═══════════════════════════════════════════════════════════════════════
# 🧊 Pruebas del KV Cache
# ═══════════════════════════════════════════════════════════════════════


class TestKVCache:
    """Pruebas para la caché de estados de atención Key-Value."""

    def test_kv_cache_store_and_retrieve(self) -> None:
        """Verifica que se pueden almacenar y recuperar estados K,V.

        Almacena estados en múltiples capas para una petición y
        comprueba que se recuperan correctamente.
        """
        cache = KVCache(max_memory_mb=100.0)

        key_states = [1.0, 2.0, 3.0]
        value_states = [4.0, 5.0, 6.0]

        result = cache.store("req-1", layer=0, key_states=key_states, value_states=value_states)
        assert result is True, "El almacenamiento debería ser exitoso"

        retrieved = cache.get("req-1", layer=0)
        assert retrieved is not None, "Los estados deberían existir en el caché"
        assert retrieved == (key_states, value_states), "Los estados recuperados deben coincidir"

    def test_kv_cache_store_multiple_layers(self) -> None:
        """Verifica el almacenamiento en múltiples capas del transformer."""
        cache = KVCache(max_memory_mb=100.0)

        for layer in range(4):
            key = [float(layer)] * 4
            value = [float(layer + 10)] * 4
            cache.store("req-1", layer=layer, key_states=key, value_states=value)

        for layer in range(4):
            retrieved = cache.get("req-1", layer=layer)
            assert retrieved is not None
            assert retrieved[0] == [float(layer)] * 4
            assert retrieved[1] == [float(layer + 10)] * 4

    def test_kv_cache_get_nonexistent(self) -> None:
        """Verifica que buscar una petición inexistente devuelve None."""
        cache = KVCache(max_memory_mb=100.0)
        assert cache.get("no-existe", layer=0) is None

    def test_kv_cache_eviction(self) -> None:
        """Verifica que la evicción elimina todos los estados de una petición.

        Almacena estados en varias capas, los evicta, y comprueba que
        ya no son accesibles. También verifica que la memoria se libera.
        """
        cache = KVCache(max_memory_mb=100.0)

        for layer in range(4):
            cache.store("req-1", layer=layer, key_states=[1.0], value_states=[2.0])

        usage_before = cache.get_memory_usage()
        assert usage_before["used_mb"] > 0, "Debería haber memoria en uso"

        freed = cache.evict("req-1")
        assert freed > 0, "Debería liberarse memoria al evictar"

        for layer in range(4):
            assert cache.get("req-1", layer=layer) is None, \
                f"La capa {layer} debería haberse eliminado"

        usage_after = cache.get_memory_usage()
        assert usage_after["used_mb"] == 0.0, "La memoria debería estar liberada"

    def test_kv_cache_evict_nonexistent(self) -> None:
        """Verifica que evictar una petición inexistente no causa error."""
        cache = KVCache(max_memory_mb=100.0)
        freed = cache.evict("no-existe")
        assert freed == 0.0

    def test_kv_cache_memory_limit(self) -> None:
        """Verifica que el caché respeta el presupuesto de memoria.

        Con un presupuesto muy pequeño, las inserciones deben fallar
        cuando se agota la memoria.
        """
        # 0.5 MB por entrada, así que con 1 MB caben exactamente 2
        cache = KVCache(max_memory_mb=1.0)

        result1 = cache.store("req-1", layer=0, key_states=[1.0], value_states=[1.0])
        assert result1 is True, "La primera inserción debería caber"

        result2 = cache.store("req-1", layer=1, key_states=[2.0], value_states=[2.0])
        assert result2 is True, "La segunda inserción debería caber"

        # La tercera NO debería caber (1.5 MB > 1.0 MB)
        result3 = cache.store("req-2", layer=0, key_states=[3.0], value_states=[3.0])
        assert result3 is False, "La tercera inserción NO debería caber"

        usage = cache.get_memory_usage()
        assert usage["used_mb"] <= cache.max_memory_mb, \
            "El uso de memoria no debe exceder el presupuesto"

    def test_kv_cache_memory_usage_stats(self) -> None:
        """Verifica que las estadísticas de uso de memoria son correctas."""
        cache = KVCache(max_memory_mb=10.0)

        usage = cache.get_memory_usage()
        assert usage["used_mb"] == 0.0
        assert usage["total_mb"] == 10.0
        assert usage["usage_percent"] == 0.0
        assert usage["num_requests_cached"] == 0

        cache.store("req-1", layer=0, key_states=[1.0], value_states=[1.0])
        usage = cache.get_memory_usage()
        assert usage["used_mb"] == 0.5
        assert usage["usage_percent"] == 5.0
        assert usage["num_requests_cached"] == 1

    def test_kv_cache_invalid_memory(self) -> None:
        """Verifica que no se puede crear un caché con memoria inválida."""
        with pytest.raises(ValueError, match="positivo"):
            KVCache(max_memory_mb=0)
        with pytest.raises(ValueError, match="positivo"):
            KVCache(max_memory_mb=-5.0)

    def test_kv_cache_update_existing_entry(self) -> None:
        """Verifica que actualizar una entrada existente no consume memoria extra."""
        cache = KVCache(max_memory_mb=10.0)

        cache.store("req-1", layer=0, key_states=[1.0], value_states=[1.0])
        usage_before = cache.get_memory_usage()["used_mb"]

        # Actualizar la misma entrada
        cache.store("req-1", layer=0, key_states=[9.0], value_states=[9.0])
        usage_after = cache.get_memory_usage()["used_mb"]

        assert usage_after == usage_before, \
            "Actualizar una entrada existente no debería gastar memoria adicional"

        # Verificar que el valor se actualizó
        retrieved = cache.get("req-1", layer=0)
        assert retrieved == ([9.0], [9.0])


# ═══════════════════════════════════════════════════════════════════════
# 📋 Pruebas del BatchScheduler
# ═══════════════════════════════════════════════════════════════════════


class TestBatchScheduler:
    """Pruebas para el planificador de batches."""

    def _make_request(
        self,
        prompt: str = "hola mundo",
        max_tokens: int = 5,
        request_id: str | None = None,
    ) -> Request:
        """Crea una petición de prueba."""
        return Request(
            id=request_id or f"req-{id(prompt)}",
            prompt=prompt,
            max_tokens=max_tokens,
            arrival_time=time.time(),
        )

    def test_batch_formation(self) -> None:
        """Verifica que las peticiones se agrupan correctamente en un batch.

        Encola varias peticiones y verifica que form_batch las agrupa
        respetando el tamaño máximo de batch.
        """
        scheduler = BatchScheduler(max_batch_size=3, max_token_budget=10000)

        for i in range(5):
            scheduler.add_request(self._make_request(
                prompt=f"petición {i}",
                request_id=f"req-{i}",
            ))

        assert scheduler.pending_count == 5

        batch = scheduler.form_batch()
        assert len(batch) == 3, "El batch no debe exceder max_batch_size"
        assert scheduler.pending_count == 2, "Deben quedar 2 peticiones en cola"

        # Todas las peticiones del batch deben estar en estado "running"
        for req in batch:
            assert req.status == "running"

    def test_batch_empty_queue(self) -> None:
        """Verifica que form_batch con cola vacía devuelve lista vacía."""
        scheduler = BatchScheduler(max_batch_size=4, max_token_budget=10000)
        batch = scheduler.form_batch()
        assert batch == []

    def test_batch_similar_lengths(self) -> None:
        """Verifica que peticiones de longitud similar se agrupan juntas.

        Envía peticiones de diferentes longitudes y comprueba que las
        de longitud similar terminan en el mismo batch, minimizando
        el padding desperdiciado.
        """
        scheduler = BatchScheduler(max_batch_size=3, max_token_budget=10000)

        # Peticiones con prompts de diferentes longitudes
        short_prompt = "hola"                                         # 1 token
        medium_prompt = "cuéntame sobre el universo y las estrellas"  # 7 tokens
        long_prompt = "explica en detalle la teoría de cuerdas y cómo se relaciona con la gravedad cuántica y el multiverso"  # 18 tokens

        scheduler.add_request(self._make_request(prompt=long_prompt, request_id="long"))
        scheduler.add_request(self._make_request(prompt=short_prompt, request_id="short"))
        scheduler.add_request(self._make_request(prompt=medium_prompt, request_id="medium"))

        batch = scheduler.form_batch()
        assert len(batch) == 3

        # El batch debería estar ordenado por longitud de prompt
        lengths = [r.prompt_length for r in batch]
        assert lengths == sorted(lengths), \
            "Las peticiones deben estar ordenadas por longitud de prompt"

    def test_batch_token_budget(self) -> None:
        """Verifica que el batch respeta el presupuesto de tokens.

        Con un presupuesto bajo, no todas las peticiones caben aunque
        haya espacio en el batch.
        """
        # Presupuesto de solo 15 tokens totales
        scheduler = BatchScheduler(max_batch_size=10, max_token_budget=15)

        # Cada petición consume ~6 tokens (1 prompt + 5 max_tokens)
        for i in range(5):
            scheduler.add_request(self._make_request(
                prompt="hola",
                max_tokens=5,
                request_id=f"req-{i}",
            ))

        batch = scheduler.form_batch()
        # Con 15 tokens de presupuesto y ~6 por petición, caben 2
        assert len(batch) <= 3, "El presupuesto de tokens debe limitar el batch"
        assert scheduler.pending_count > 0, "Algunas peticiones deben quedar en cola"

    def test_batch_scheduler_invalid_params(self) -> None:
        """Verifica la validación de parámetros del scheduler."""
        with pytest.raises(ValueError):
            BatchScheduler(max_batch_size=0, max_token_budget=100)
        with pytest.raises(ValueError):
            BatchScheduler(max_batch_size=4, max_token_budget=0)


# ═══════════════════════════════════════════════════════════════════════
# 🎲 Pruebas del TokenGenerator
# ═══════════════════════════════════════════════════════════════════════


class TestTokenGenerator:
    """Pruebas para el generador simulado de tokens."""

    def test_generate_token(self) -> None:
        """Verifica que el generador produce tokens del vocabulario."""
        gen = TokenGenerator()
        token = gen.generate_token()
        assert isinstance(token, str), "El token debe ser un string"
        assert token in gen.vocabulary, "El token debe pertenecer al vocabulario"

    def test_generate_multiple_tokens(self) -> None:
        """Verifica que se pueden generar múltiples tokens consecutivos."""
        gen = TokenGenerator()
        tokens = [gen.generate_token() for _ in range(100)]
        assert len(tokens) == 100
        assert all(t in gen.vocabulary for t in tokens)


# ═══════════════════════════════════════════════════════════════════════
# 🔮 Pruebas del InferenceServer
# ═══════════════════════════════════════════════════════════════════════


class TestInferenceServer:
    """Pruebas para el servidor de inferencia completo."""

    def test_submit_request(self) -> None:
        """Verifica que se pueden enviar peticiones al servidor."""
        server = InferenceServer()
        rid = server.submit_request("¿Hola cosmos?", max_tokens=5)
        assert isinstance(rid, str)
        assert len(rid) > 0

        request = server.get_request(rid)
        assert request is not None
        assert request.prompt == "¿Hola cosmos?"
        assert request.max_tokens == 5
        assert request.status == "pending"

    def test_submit_invalid_request(self) -> None:
        """Verifica la validación de peticiones inválidas."""
        server = InferenceServer()
        with pytest.raises(ValueError, match="vacío"):
            server.submit_request("", max_tokens=5)
        with pytest.raises(ValueError, match="vacío"):
            server.submit_request("   ", max_tokens=5)
        with pytest.raises(ValueError, match="max_tokens"):
            server.submit_request("hola", max_tokens=0)

    def test_inference_step(self) -> None:
        """Verifica que un paso de inferencia genera tokens correctamente.

        Envía una petición, ejecuta un paso y comprueba que se generó
        exactamente un token.
        """
        server = InferenceServer(max_batch_size=4)
        rid = server.submit_request("consulta al oráculo", max_tokens=5)

        result = server.step()
        assert result["tokens_generated"] == 1, "Debe generar 1 token por petición"
        assert result["batch_size"] == 1

        request = server.get_request(rid)
        assert request is not None
        assert request.tokens_generated == 1
        assert len(request.output_tokens) == 1
        assert request.status == "running"

    def test_inference_step_empty(self) -> None:
        """Verifica que un paso sin peticiones no genera nada."""
        server = InferenceServer()
        result = server.step()
        assert result["tokens_generated"] == 0
        assert result["batch_size"] == 0

    def test_request_completion(self) -> None:
        """Verifica que las peticiones se completan tras generar max_tokens.

        Ejecuta suficientes pasos para que una petición de 3 tokens se
        complete, y verifica que su estado cambia a 'completed'.
        """
        server = InferenceServer(max_batch_size=4)
        rid = server.submit_request("breve consulta", max_tokens=3)

        completed = False
        for _ in range(10):  # Máximo 10 pasos de seguridad
            result = server.step()
            if rid in result["completed"]:
                completed = True
                break

        assert completed, "La petición debería haberse completado"

        request = server.get_request(rid)
        assert request is not None
        assert request.status == "completed"
        assert request.tokens_generated == 3
        assert len(request.output_tokens) == 3

    def test_streaming_response(self) -> None:
        """Verifica que el streaming devuelve tokens incrementalmente.

        Genera tokens y luego los consume vía streaming, comprobando
        que se reciben en el orden correcto.
        """
        server = InferenceServer(max_batch_size=4)
        rid = server.submit_request("streaming test", max_tokens=5)

        # Ejecutar todos los pasos
        for _ in range(10):
            server.step()

        # Consumir vía streaming
        tokens = list(server.stream_response(rid))
        assert len(tokens) == 5, "Deberían haberse transmitido 5 tokens"
        assert all(isinstance(t, str) for t in tokens)

        # Verificar que coinciden con los tokens generados
        request = server.get_request(rid)
        assert request is not None
        assert tokens == request.output_tokens

    def test_streaming_nonexistent_request(self) -> None:
        """Verifica que el streaming de una petición inexistente lanza error."""
        server = InferenceServer()
        with pytest.raises(KeyError, match="no encontrada"):
            list(server.stream_response("no-existe"))

    def test_server_stats(self) -> None:
        """Verifica que las estadísticas del servidor son correctas.

        Envía peticiones, ejecuta pasos y comprueba que los contadores
        reflejan la actividad real.
        """
        server = InferenceServer(max_batch_size=4, kv_cache_size_mb=50.0)

        # Estado inicial
        stats = server.get_stats()
        assert stats["total_requests"] == 0
        assert stats["total_tokens_generated"] == 0
        assert stats["total_steps"] == 0

        # Enviar peticiones
        server.submit_request("petición uno", max_tokens=3)
        server.submit_request("petición dos", max_tokens=3)

        stats = server.get_stats()
        assert stats["total_requests"] == 2
        assert stats["pending_requests"] == 2

        # Ejecutar un paso
        server.step()
        stats = server.get_stats()
        assert stats["total_steps"] == 1
        assert stats["total_tokens_generated"] == 2  # 1 token × 2 peticiones
        assert stats["throughput_tokens_per_step"] == 2.0
        assert stats["model_name"] == "oraculo-galactico-7B"
        assert "kv_cache_usage" in stats

    def test_multiple_concurrent_requests(self) -> None:
        """Verifica el manejo de muchas peticiones simultáneas.

        Envía 20 peticiones y ejecuta pasos hasta que todas se completen,
        verificando que el servidor maneja correctamente el batching y
        la cola de espera.
        """
        server = InferenceServer(max_batch_size=4, kv_cache_size_mb=200.0)

        request_ids: list[str] = []
        for i in range(20):
            rid = server.submit_request(
                prompt=f"consulta número {i} al oráculo galáctico",
                max_tokens=3,
            )
            request_ids.append(rid)

        assert server.scheduler.pending_count == 20

        # Ejecutar hasta completar todas (con límite de seguridad)
        all_completed: set[str] = set()
        for _ in range(100):
            result = server.step()
            all_completed.update(result["completed"])
            if len(all_completed) == 20:
                break

        assert len(all_completed) == 20, \
            f"Todas las peticiones deben completarse. Completadas: {len(all_completed)}/20"

        # Verificar cada petición
        for rid in request_ids:
            request = server.get_request(rid)
            assert request is not None
            assert request.status == "completed"
            assert request.tokens_generated == 3

        # Verificar estadísticas finales
        stats = server.get_stats()
        assert stats["completed_requests"] == 20
        assert stats["total_tokens_generated"] == 60  # 20 × 3 tokens
        assert stats["pending_requests"] == 0

    def test_mixed_token_lengths(self) -> None:
        """Verifica que peticiones con diferentes max_tokens se manejan bien.

        Peticiones con diferentes longitudes deben completarse en
        momentos distintos, y las más cortas liberan su KV Cache antes.
        """
        server = InferenceServer(max_batch_size=8, kv_cache_size_mb=100.0)

        rid_short = server.submit_request("corta", max_tokens=1)
        rid_long = server.submit_request("larga", max_tokens=5)

        # Primer paso: ambas generan 1 token, la corta se completa
        result = server.step()
        assert rid_short in result["completed"], "La petición corta debe completarse en 1 paso"
        assert rid_long not in result["completed"]

        req_short = server.get_request(rid_short)
        assert req_short is not None
        assert req_short.status == "completed"

        req_long = server.get_request(rid_long)
        assert req_long is not None
        assert req_long.status == "running"

    def test_kv_cache_freed_on_completion(self) -> None:
        """Verifica que el KV Cache se libera al completar una petición."""
        server = InferenceServer(max_batch_size=4, kv_cache_size_mb=100.0)
        rid = server.submit_request("test liberación caché", max_tokens=2)

        # Primer paso: genera token, KV Cache en uso
        server.step()
        cache_usage = server.kv_cache.get_memory_usage()
        assert cache_usage["num_requests_cached"] >= 1

        # Segundo paso: se completa, KV Cache liberado
        server.step()
        request = server.get_request(rid)
        assert request is not None
        assert request.status == "completed"

        cache_usage = server.kv_cache.get_memory_usage()
        assert cache_usage["num_requests_cached"] == 0, \
            "El KV Cache debe liberarse al completar la petición"

    def test_continuous_batching(self) -> None:
        """Verifica el batching continuo: nuevas peticiones entran al batch.

        Envía peticiones en diferentes momentos y verifica que las nuevas
        se incorporan al batch en pasos posteriores.
        """
        server = InferenceServer(max_batch_size=4, kv_cache_size_mb=100.0)

        # Primera tanda
        server.submit_request("primera tanda", max_tokens=3)
        server.step()

        # Segunda tanda — debe incorporarse al batch
        server.submit_request("segunda tanda", max_tokens=3)
        result = server.step()
        assert result["batch_size"] == 2, \
            "Las nuevas peticiones deben incorporarse al batch existente"
