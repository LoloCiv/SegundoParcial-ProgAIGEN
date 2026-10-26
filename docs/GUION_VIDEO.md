# Guion del video

Escrito largo a propósito: leído completo dura unos 18 minutos, más del doble de lo permitido. Los tiempos de cada escena son el objetivo después de recortar (8 minutos en total). Los párrafos marcados *(Opcional)* son los primeros para recortar. La consigna pide entre 5 y 8 minutos.

## 1. Carátula e introducción (0:00 a 0:45)

**Mostrar:**

1. Abrí `docs/caratula.html` en el navegador y poné F11 (pantalla completa).
2. Cuando digas «Ahora le doy una vuelta de tuerca», cambiá a la segunda carátula: `docs/caratula2.html` (también con F11). Ahí se ven los dos modelos, sus archivos y sus skills mientras lo explicás.
3. Si usás el párrafo opcional del diagrama, terminá mostrando el de la sección **Visión general** de esta guía.

**Decir:**

> Hola, ¿cómo están? Mi nombre es Laureano Civetta, estoy cursando Ingeniería en Inteligencia Artificial, y este es mi segundo parcial de Programación con IA Generativa.

> Para este parcial decidí tomar como base la idea del primero. En el Parcial 1 había armado una plataforma de juegos por turnos donde yo jugaba contra una inteligencia artificial: el agente se conectaba al juego a través de un servidor MCP, y desde el chat yo le pedía que jugara su turno.

> Ahora le doy una vuelta de tuerca: en lugar de jugar yo contra la IA, pongo a dos agentes de inteligencia artificial a jugar entre ellos al Cuatro en Línea. Y los dos corren de forma local, en mi propia computadora, con Ollama: uno usa el modelo Llama, de Meta, y el otro usa Qwen, de Alibaba.

> La idea es responder dos preguntas: ¿qué modelo juega mejor?, y ¿cuánto cambia el comportamiento de un agente si le cambio las instrucciones? Para eso, cada agente está definido en un archivo Markdown, y su forma de jugar (agresiva, defensiva o equilibrada) sale de unas skills, también en Markdown, que puedo intercambiar sin tocar una sola línea de código.

> Como dimensiones complementarias elegí pruebas, unitarias y de integración, y documentación técnica, que vamos a generar en vivo con otro agente al final del video.

> *(Opcional)* En este diagrama se ve el recorrido de una jugada. El orquestador le pide la jugada al agente. El agente arma el prompt con sus skills y el estado del tablero, y se lo manda a Ollama. Ollama se lo pasa al modelo, el modelo responde con un JSON que dice qué columna eligió, y el código valida que esa jugada sea legal antes de aplicarla.

**Consejo:** La consigna permite como máximo un minuto de introducción con diapositivas. Si te pasás, el párrafo del diagrama es el primero para cortar.

## 2. Ollama y los modelos (0:45 a 1:45)

**Mostrar:**

1. Terminal de PowerShell abierta en la carpeta `Parcial2`.
2. Mostrá el comando de instalación (no hace falta ejecutarlo) y después ejecutá `ollama --version`.
3. Ejecutá los dos `ollama pull`: como ya están descargados, Ollama dice que están al día.
4. Ejecutá `ollama list` para ver los modelos y cuánto pesan.
5. Opcional: hacele una pregunta a Qwen desde la terminal y después ejecutá `ollama ps` para mostrar que quedó cargado en la GPU.

```powershell
irm https://ollama.com/install.ps1 | iex
ollama --version
ollama pull llama3
ollama pull qwen2.5:7b
ollama list
ollama run qwen2.5:7b "Explicame en una frase qué es el Cuatro en Línea"
ollama ps
```

**Decir:**

> Empecemos por el motor. Para correr los modelos de forma local uso Ollama. Ollama es un programa que descarga modelos de lenguaje abiertos y los ejecuta en tu propia máquina: no hay nube de por medio, no hay costo por consulta y los datos nunca salen de la computadora.

> La instalación en Windows es una sola línea en PowerShell, esta de acá. Yo ya lo tengo instalado, así que simplemente verifico la versión con `ollama --version`.

> Algo importante: una vez instalado, Ollama queda corriendo como un servidor local en el puerto 11434. Eso es clave, porque después mi código se va a comunicar con los modelos mandándole pedidos HTTP justamente a ese puerto.

> Ahora descargo los modelos con `ollama pull`. Primero Llama 3, de Meta, que tiene 8 mil millones de parámetros. Después Qwen 2.5, de Alibaba, en su versión de 7 mil millones. Como ya los tengo descargados, Ollama me avisa que están actualizados.

> Elegí estos dos a propósito: son de tamaño parecido, así que la comparación es justa. Y vienen cuantizados, es decir, comprimidos a 4 bits. Por eso pesan unos 4,7 GB cada uno y entran en la memoria de mi placa de video, una RTX 3060 de 12 GB. Esto es lo que vimos en la clase 8: se pierde un poco de precisión a cambio de poder correr el modelo en una computadora común.

> Con `ollama list` veo los modelos instalados y lo que pesa cada uno.

> *(Opcional)* Y para chequear que funcionan, le hago una pregunta rápida a Qwen directamente desde la terminal... ahí está la respuesta. Con `ollama ps` veo que el modelo quedó cargado en la GPU, listo para responder rápido.

**Consejo:** La primera respuesta de un modelo tarda más porque se está cargando en la placa de video. Hacé la pregunta de prueba antes de grabar, así en cámara responde al instante.

## 3. Los agentes declarativos (1:45 a 2:45)

**Mostrar:**

1. En VS Code, mostrá el árbol de carpetas: `agents/`, `skills/`, `src/arena/`, `tests/`, `docs/`.
2. Abrí `agents/jugador_qwen.agent.md`. Señalá el bloque entre `---`: `model`, `options` y `skills`.
3. Abrí `agents/jugador_llama.agent.md` al lado (pantalla dividida) para que se vea que son iguales salvo el nombre y el modelo.

**Decir:**

> Pasemos al código. Esta es la estructura del proyecto. Las dos carpetas más importantes son `agents` y `skills`, porque son las que definen a los agentes de forma declarativa, que es justamente lo que pide la consigna.

> Abro el agente de Qwen. Es un archivo Markdown con un encabezado en YAML, lo que se llama frontmatter, entre estas tres rayitas. Ahí declaro el nombre del agente, una descripción de cuándo usarlo, el modelo de Ollama que va a usar (en este caso `qwen2.5:7b`) y los parámetros del modelo.

> Estos parámetros son los que vimos en la clase 8. `temperature` controla qué tan creativo o aleatorio es el modelo al elegir la siguiente palabra: con 0.4 juega de forma bastante consistente. `num_ctx` es la ventana de contexto, la memoria de corto plazo del modelo: 4096 tokens alcanzan para las instrucciones, el tablero y los reintentos. `num_predict` limita cuánto puede responder, para que no se ponga a escribir párrafos. `top_p` descarta las opciones menos probables. Y `seed` es la semilla, para que los resultados sean reproducibles.

> Más abajo, en `skills`, declaro qué habilidades tiene el agente: una para el formato de la respuesta, otra para analizar amenazas y una de personalidad, en este caso equilibrado.

> Y después del frontmatter viene el cuerpo, que funciona como prompt de sistema: el rol del agente, el contexto (cómo es el tablero, cómo se gana) y las restricciones estrictas, por ejemplo, que solo puede elegir columnas legales y que no puede escribir nada fuera del JSON.

> Si abro el agente de Llama al lado, se ve que es exactamente igual: lo único que cambia es el nombre y el modelo. Eso es lo que hace justa la comparación: mismas instrucciones, mismos parámetros, distinto modelo.

> *(Opcional)* Como vimos en la clase 9, este archivo es la customización, la declaración. El agente propiamente dicho es lo que existe en tiempo de ejecución, cuando el programa lee este archivo y le pasa estas reglas al modelo.

## 4. Las skills (2:45 a 3:30)

**Mostrar:**

1. Abrí `skills/utilidad/formato_jugada.skill.md` y `skills/utilidad/analisis_amenazas.skill.md`.
2. Abrí `skills/personalidad/agresivo.skill.md` y `defensivo.skill.md` lado a lado. Señalá las secciones: Rol, Objetivo, Estilo de decisión y Restricciones.

**Decir:**

> Ahora las skills, que son el corazón del proyecto. Una skill es una capacidad empaquetada y reutilizable: tiene un nombre, un objetivo, qué entrada recibe, qué salida tiene que producir y qué restricciones debe respetar. Es la estructura que vimos en clase.

> Tengo dos tipos. Las de utilidad, que usan todos los agentes. `formato_jugada` fija el contrato de salida: el modelo tiene que responder un único JSON con la columna, del 1 al 7, y una razón breve. Y `analisis_amenazas` le da un orden de prioridades: si puede ganar, gana; si el rival está por ganar, lo bloquea; y si no hay nada urgente, decide según su personalidad.

> Y después están las de personalidad. Acá tengo agresivo y defensivo lado a lado. El agresivo busca extender su línea más larga, ocupar el centro y crear dobles amenazas, aunque tenga que asumir riesgos. El defensivo hace lo contrario: prioriza tapar las líneas del rival y evita cualquier jugada que le regale la victoria. Hay un tercero, equilibrado, que alterna entre las dos cosas.

> Lo interesante es que cada agente tiene una sola skill de personalidad, y la puedo cambiar desde la interfaz o desde la terminal sin tocar código. El programa saca la personalidad anterior, pone la nueva, y las de utilidad quedan igual. Es decir: mismo modelo, distinto comportamiento, cambiando solamente un archivo Markdown.

## 5. La conexión con Ollama (3:30 a 4:20)

**Mostrar:**

1. Abrí `src/arena/ollama_client.py` y bajá hasta el método `chat`: mostrá el `request_body` y la línea del `post`.
2. Abrí `src/arena/agent.py`: mostrá `build_system_prompt`, `build_turn_prompt` y el bucle `for` de `choose_move`.

**Decir:**

> ¿Y cómo se conecta todo esto con el modelo? Este es el archivo `ollama_client.py`, que es el único que habla con Ollama. Lo que hace es armar un pedido HTTP y mandarlo al servidor local, a `localhost:11434/api/chat`.

> En el cuerpo del pedido va el nombre del modelo y los mensajes: el prompt de sistema, con el rol y las skills, y el mensaje con el tablero. Y además estas opciones: `stream` en false, para recibir la respuesta completa de una vez; `format json`, para obligar al modelo a responder en JSON; `keep_alive`, para que el modelo quede cargado en memoria entre jugada y jugada; y los parámetros que leímos del archivo del agente.

> De la respuesta me quedo con el texto que generó el modelo y con dos contadores: cuántos tokens leyó y cuántos generó. También mido cuánto tardó. Si Ollama está apagado o responde algo inesperado, lanzo un error con un mensaje claro.

> El que usa este cliente es `agent.py`. En cada turno arma dos cosas: el prompt de sistema, que junta el rol del agente con el texto de cada skill, y el prompt del turno, que tiene el tablero dibujado en texto, las columnas legales y dos listas que calcula el propio código: con qué columnas gana ahora mismo y qué columnas tiene que bloquear.

> Y acá está la parte clave: el modelo propone una columna, pero el que decide si es válida es el código. Si el modelo responde algo que no es JSON, o elige una columna llena, le devuelvo el error y le pido que corrija, hasta dos veces. Si aun así falla, el programa juega una columna legal al azar para que la partida no se rompa, y lo registra como fallback. Esas jugadas inválidas después son una métrica más para comparar a los modelos.

**Consejo:** Si te sobra tiempo, la sección **Archivos clave** de esta guía tiene el JSON exacto que se envía y el que vuelve.

## 6. Pruebas unitarias y de integración (4:20 a 5:15)

**Mostrar:**

1. En VS Code, desplegá la carpeta `tests`: se ven `unit`, `integration` y `conftest.py`.
2. En `unit`, abrí los cuatro archivos uno por uno mientras hablás: `test_engine.py`, `test_parser.py`, `test_skills.py` y `test_agent.py`. No hace falta leerlos enteros: con los nombres de los tests alcanza.
3. Abrí `tests/conftest.py` y señalá la clase `ClienteOllamaFalso`.
4. En `integration`, abrí `test_partida.py` y bajá siguiendo la tabla de abajo, de arriba a abajo del archivo.
5. Al final, en la terminal: `pytest -v`.

```powershell
pytest -v
pytest -m ollama
```

**Decir:**

> Pasemos a las pruebas, que son una de las dos dimensiones complementarias que elegí. Están todas en la carpeta `tests`, separadas en dos: `unit`, para las pruebas unitarias, e `integration`, para las de integración. Los nombres de los tests están escritos como frases, así que con solo leerlos se entiende qué verifica cada uno.

> Arranquemos por `unit`. Acá cada archivo prueba una pieza del proyecto por separado, y todos siguen el patrón AAA: Arrange, Act, Assert, o sea preparar, ejecutar y comprobar. Lo van a ver marcado con comentarios dentro de cada test.

> En `test_engine` están las pruebas del motor del juego: que la ficha caiga hasta abajo y cambie el turno, y que cuatro en vertical o en diagonal ganen la partida. Y también los casos de error: si intento jugar en una columna llena, o en una que no existe, el motor tiene que lanzar una excepción. Este último prueba cuatro entradas inválidas con un solo test: una columna negativa, una fuera del tablero, un texto y un valor vacío.

> En `test_parser` pruebo la parte que interpreta lo que responde el modelo: que lea bien un JSON limpio, que tolere texto alrededor, porque a veces el modelo agrega un "¡claro!" antes de la respuesta, y que rechace las respuestas que no sirven: vacías, sin columna, mal escritas o con una columna fuera del 1 al 7.

> En `test_skills` pruebo la lectura de los archivos Markdown: que el agente de Qwen se lea con su modelo, sus parámetros y sus skills; que se carguen las cinco skills del proyecto; que una skill mal escrita, sin el campo tipo, dé un error claro; y que al cambiar la personalidad se reemplace solo esa skill y las demás queden igual.

> Y en `test_agent` pruebo al agente que decide: que con una respuesta válida devuelva la columna; que si el modelo elige una columna llena se le vuelva a preguntar mostrándole el error; que si responde basura tres veces juegue al azar en vez de romperse; y que el prompt lleve el rol y todas las skills.

> ¿Y cómo pruebo el agente sin usar el modelo real? Con este archivo, `conftest.py`. Acá está la clase `ClienteOllamaFalso`: un Ollama de mentira que responde lo que yo le programo y anota cada consulta que recibe. Es lo que se llama un doble de prueba, o mock. Gracias a eso las pruebas son rápidas y dan siempre el mismo resultado.

**Integration: recorriendo `test_partida.py` de arriba a abajo**

> Ahora `integration`. Acá ya no pruebo piezas sueltas: junto todo y juego partidas. Abro `test_partida.py` y lo recorro.

| En el código | Qué decís |
|---|---|
| `def jugada(columna)` | Esta función chiquita arma lo que contestaría el modelo: un JSON con la columna. Con ella le escribo el guion a cada jugador. |
| Los parámetros `carpeta_agentes` y `cliente_falso` | Vienen de `conftest.py`. Uno es la carpeta de los `.md` y el otro es el `ClienteOllamaFalso` que mostré recién. pytest se los pasa solo a cada test. |
| `test_una_partida_completa_termina_con_un_ganador` | Armo a Llama y a Qwen desde sus archivos con `build_agent`, pero con el Ollama falso: Llama juega siempre la columna 1 y Qwen la 2, la 3 y la 4. Corro `play_match` y Llama gana en siete jugadas, cuatro en vertical. |
| `test_la_partida_sigue_aunque_el_modelo_responda_basura` | Acá Llama contesta "no", "sé", "jugar". La partida no se corta: esa jugada queda marcada como fallback, con tres intentos inválidos, y la partida termina igual. |
| `test_cambiar_la_skill_cambia_el_prompt_que_recibe_el_modelo` | El mismo agente, una vez agresivo y otra defensivo. Miro el prompt que le llegó a cada uno: uno tiene solo el texto agresivo y el otro solo el defensivo. O sea, la skill llega de verdad al modelo. |
| `test_los_parametros_cambiados_llegan_al_modelo` | Subo la temperatura a 1.2, como desde la interfaz, y llega así al modelo. `num_ctx` sigue en 4096, como en el archivo. |
| `test_el_torneo_alterna_quien_empieza_y_calcula_metricas` | Llama contra `MinimaxPlayer`, el rival sin IA. Dos partidas: en la primera abre Llama, en la segunda abre minimax, y `summarize` devuelve partidas, victorias y derrotas. |
| `class SesionHttpFalsa` y `class RespuestaHttpFalsa` | Estas dos clases reemplazan a la librería `requests`. `SesionHttpFalsa` guarda el pedido que le mandan y `RespuestaHttpFalsa` hace de Ollama contestando, incluso con un error 500. Así pruebo la conexión sin tener Ollama prendido. |
| `test_el_cliente_ollama_arma_bien_el_pedido` | Verifico que el pedido vaya a `localhost:11434/api/chat`, sin streaming y pidiendo JSON, y que se lean bien los tokens de la respuesta. |
| `@pytest.mark.parametrize` sobre `test_las_fallas_de_ollama_se_informan_como_ollama_error` | `parametrize` hace que este test corra tres veces, una por caso: Ollama apagado, error 500 y respuesta incompleta. En los tres tiene que salir un `OllamaError`, un error claro en vez de que el programa explote. |
| `@pytest.mark.ollama` sobre `test_partida_real_entre_llama_y_qwen` | Esta marca separa la única prueba que usa los modelos de verdad: juega una partida real Llama contra Qwen. Por defecto se saltea, porque así lo configuré en `pyproject.toml`, y la corro a mano con `pytest -m ollama`. |

**Decir al final:**

> Y para cerrar corro todo con `pytest -v`: pasan las 35 en menos de un segundo, cada una con su nombre.

> *(Opcional)* Un dato: cuando escribí la prueba de las métricas del torneo, falló, y gracias a eso encontré un error real en el código, que ya está corregido. Para eso sirven las pruebas.

**Consejo:** Si se te hace largo, en `unit` abrí solo `test_engine.py` y `test_agent.py`, y nombrá los otros dos. En integración, las filas de la partida con basura y de los parámetros son las primeras para saltear.

## 7. Partida en vivo y ajuste de parámetros (5:15 a 6:15)

**Mostrar:**

1. Terminal: ejecutá `streamlit run app.py` y abrí la pestaña que se abre en el navegador.
2. Barra lateral, Jugador 1: `jugador_llama.agent.md` con skill `agresivo`. Jugador 2: `jugador_qwen.agent.md` con skill `defensivo`.
3. Pestaña **Partida en vivo**: tocá **Jugar partida** y dejá correr unas jugadas mientras hablás.
4. Al terminar, subí la `temperature` del Jugador 1 a 1.2 y jugá otra partida.

```powershell
streamlit run app.py
```

**Decir:**

> Ahora sí, veamos a los agentes en acción. Levanto la interfaz con `streamlit run app.py`.

> En la barra lateral configuro cada jugador: elijo el archivo del agente, la skill de personalidad y los parámetros del modelo. Pongo a Llama agresivo, con las fichas rojas, contra Qwen defensivo, con las amarillas. Y arranco la partida.

> Fíjense que en cada jugada se ve qué columna eligió, cuánto tardó, si cometió jugadas inválidas y la razón que da el propio modelo. Ahí se nota la personalidad: el agresivo habla de construir su línea, y el defensivo de frenar la del rival.

> *(Opcional)* Una cosa que vi en las pruebas: a veces Llama ignora la lista de columnas que tiene que bloquear, aunque la tiene escrita en el prompt. Es un modelo de 8 mil millones de parámetros y no siempre sigue todas las instrucciones.

> Ahora cambio un parámetro interno del modelo: subo la temperatura de Llama a 1.2 y juego de nuevo. Con temperatura alta el modelo elige con más azar, así que sus jugadas se vuelven más erráticas y pueden aumentar las jugadas inválidas. Entonces puedo afinar a los agentes de dos maneras: con las skills, que cambian qué le pido, y con los parámetros, que cambian cómo genera la respuesta.

**Consejo:** Cada jugada tarda unos 3 segundos. Aprovechá esa espera para hablar en vez de quedarte en silencio.

## 8. Torneo y conclusiones (6:15 a 6:50)

**Mostrar:**

1. Pestaña **Torneo y métricas** con un torneo ya corrido antes de grabar (6 partidas), o la salida del comando de torneo en la terminal.

```powershell
python arena_cli.py tournament --a llama --b qwen --a-estilo agresivo --b-estilo defensivo --games 6
```

**Decir:**

> Para comparar en serio armé un modo torneo: varias partidas seguidas, alternando quién empieza para no favorecer al que mueve primero, y con una semilla distinta en cada partida para que no se repitan.

> En un torneo de seis partidas, Qwen ganó cinco y Llama una. Casi no hubo jugadas inválidas, y la velocidad fue prácticamente la misma: unos 2,6 segundos por jugada. Y cuando invertí los estilos, Llama defensivo contra Qwen agresivo, Qwen volvió a ganar.

> La conclusión es interesante: en este juego pesa más el modelo que la personalidad. Las skills cambian cómo razona y lo que dice el agente, pero Qwen sigue mejor las instrucciones tácticas, como bloquear al rival.

**Consejo:** Si en tu torneo los números salen distintos, decí los tuyos: con semillas distintas cada corrida varía un poco.

## 9. Documentación en vivo (6:50 a 7:40)

**Mostrar:**

1. En VS Code, abrí el chat y elegí el agente **Documentador** en el selector de modos.
2. Pegá el prompt del plan (sección **Documentación en vivo** de esta guía) y mostrá la respuesta.
3. Pegá el prompt de documentación de `agent.py`. Abrí el `docs/agent.md` generado.
4. Terminal: `pytest` para mostrar que siguen todas en verde.

```powershell
pytest
```

**Decir:**

> Por último, la segunda dimensión complementaria: la documentación técnica. Para eso tengo otro agente declarado, el Documentador, en la carpeta `.github/agents`. Lo selecciono en el chat de VS Code.

> Siguiendo lo que vimos en la clase 7, no le pido solamente "documentá esto": le doy un rol y una audiencia, le indico el formato estándar (docstrings PEP 257 y Markdown), le pido precondiciones, postcondiciones y excepciones, y que separe la lógica de decisión de las llamadas a infraestructura.

> Primero le pido un plan, para ver qué va a hacer antes de que toque ningún archivo... Y ahora le pido que lo haga.

> Acá está el documento generado, con el flujo paso a paso, la tabla de funciones y una analogía para explicar el mecanismo de reintento. Y vuelvo a correr las pruebas para demostrar que no cambió la lógica: siguen todas en verde.

**Consejo:** Si el agente tarda mucho en cámara, dejá el documento generado de antemano y mostrá solo el prompt y el resultado.

## 10. Cierre (7:40 a 7:55)

**Mostrar:**

1. Volvé a la carátula o dejá la interfaz con el tablero final en pantalla.

**Decir:**

> Y eso es todo. En resumen: dos agentes locales configurados de forma declarativa, con skills intercambiables, que se enfrentan en Cuatro en Línea y se comparan con métricas; respaldados por pruebas unitarias y de integración, y documentados con la ayuda de otro agente.

> Todo el código, los archivos de los agentes y las skills, las pruebas y el README para reproducir el entorno están en el repositorio. Muchas gracias.
