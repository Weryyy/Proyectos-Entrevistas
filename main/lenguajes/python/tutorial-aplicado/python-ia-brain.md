# 🐍 Python Aplicado: Inteligencia Artificial y Machine Learning

Este tutorial se enfoca en cómo utilizar Python como el cerebro de sistemas inteligentes, basándose en los conocimientos del **Módulo 9 (RL)** y **Módulo 11 (Vector Search)**.

---

## 🧠 Python for IA Brain

### 1. Aprendizaje por Refuerzo (RL)
En el Módulo 9, usamos Python para implementar el algoritmo **Q-Learning**. La clave aquí es la gestión del estado y la actualización de la tabla Q.

```python
# Ejemplo: Actualización de la regla de Bellman
q_table[state, action] = q_table[state, action] + alpha * (reward + gamma * np.max(q_table[next_state]) - q_table[state, action])
```

### 2. Búsqueda Vectorial (Embeddings)
En el Módulo 11, transformamos texto en vectores matemáticos. Python destaca aquí por su ecosistema de librerías como `numpy` para cálculos matriciales rápidos.

```python
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
```

---

## 🚀 Ampliación y Escalabilidad (Tecnología de última hora)

### Mejoras Modernas (2025-2026):
1. **Pydantic AI**: Utilizar validación de datos estricta para los agentes de IA. En lugar de procesar strings puros de un LLM, forzar esquemas JSON.
2. **LoRA & Quantization**: Para escalar el Módulo 4 (Inferencia), en lugar de cargar modelos completos, usar adaptadores LoRA para reducir el consumo de VRAM de 16GB a menos de 4GB.

### Cambios para Escalabilidad:
- **Vector DBs Externas**: En lugar de guardar vectores en memoria (`list`), usar infraestructuras como **Pinecone** o **Milvus** que permiten buscar entre billones de documentos en milisegundos.
- **AsyncIO en IA**: Para agentes multimodales, usar `asyncio` para que el agente pueda "pensar" mientras espera la respuesta de una API de visión o audio.
