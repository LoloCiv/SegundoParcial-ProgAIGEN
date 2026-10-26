# Cliente de Ollama

## Propósito

[`ollama_client.py`](../src/arena/ollama_client.py) encapsula las solicitudes
HTTP al servidor local de Ollama. Usa por defecto `http://localhost:11434`,
envía chats sin streaming con formato JSON y obtiene la lista de modelos
descargados.

## Flujo paso a paso

1. `OllamaClient` conserva el host sin la barra final, el timeout de chat y un
   transporte HTTP. Si no se inyecta uno, usa `requests`.
2. `chat(model, messages, options)` envía un POST a `/api/chat` con
   `stream=False`, `format="json"` y `keep_alive="10m"`.
3. Mide la duración y extrae contenido y contadores de tokens de la respuesta.
4. `list_models()` consulta `/api/tags` y devuelve los nombres reportados.

## API pública

| Elemento | Descripción |
| --- | --- |
| `OllamaClient(host, timeout, session)` | Cliente para los endpoints locales. |
| `OllamaClient.chat(model, messages, options)` | Consulta un modelo y devuelve `ChatResult`. |
| `OllamaClient.list_models()` | Devuelve los nombres de modelos instalados. |
| `ChatResult` | Contenido y métricas de una consulta. |
| `OllamaError` | Error de ejecución para fallos o respuestas inesperadas. |

## Ejemplo mínimo

Requiere que Ollama esté accesible en el host configurado y que el modelo
solicitado esté disponible:

```python
from arena.ollama_client import OllamaClient

cliente = OllamaClient()
respuesta = cliente.chat(
    "llama3:latest",
    [{"role": "user", "content": "Respondé con un JSON breve."}],
)
print(respuesta.content, respuesta.latency_s)
```

## Errores posibles

`OllamaClient.chat` y `list_models` convierten fallos HTTP de `requests`,
errores de decodificación JSON y algunas estructuras incompletas en
`OllamaError`. El timeout explícito de 180 segundos se configura para chat; el
listado de modelos usa 10 segundos. Un modelo inexistente o un servidor apagado
se informan como error de consulta, no como una respuesta vacía.
