## Parte Teorica
### Pregunta 1: ¿Porque git Git es un DAG? explicar con referencias al diseño interno de Git y justifica por que no puede haber ciclos, razona como esto garantiza la terminacion de algoritmos de busqueda de rutas

Git es un DAG porque cada commit apunta a sus commits padre, pero nunca va a poder apuntar hacia adelante o crear un ciclo. Esto pasa por como funciona internamente:

- Cada commit tiene un hash SHA-1 que se calcula con el contenido del commit y los hash de sus padres
- Una vez que se crea un commit es inmutable, no se puede cambiar
- Los commits solo pueden referenciar a commits que ya existen antes

No puede haber ciclos porque seria imposible, por ejemplo para que el commit A apunte al commit B, B ya debe existir. Pero si B quiere apuntar de vuelta a A, A ya tendria que existir antes que B, lo cual es contradictorio e imposible.

Y esto garantiza que los algoritmos terminen porque siempre hay un "final",eventualmente llegaremos a commits que no tienen padres (por ejemplo, el primer commit del repositorio). Cuando hacemos git log o buscamos rutas, git no puede quedarse en un loop infinito.

### Pregunta 2: Contrasta ambos patrones en el marco de una malla de microservicios. ¿Porque Mediator brinda mejor desacoplamiento y facilita la inyeccion de logica de back-pressure, en lugar de usar un simple Adapter para transformaciones de mensajes?

El patron Adapter solo se encarga de convertir un formato de mensaje a otro (como JSON a XML). Es util pero limitado.

En cambio el patron Mediator es mas poderoso porque:

**Mejor desacoplamiento:**
- Con Adapter los servicios aun necesitan conocer a quien enviar mensajes
- Con Mediator los servicios solo hablan con el mediator, no saben que otros servicios existen
- Si quiero agregar un nuevo servicio, con Mediator solo lo conecto al mediator y no tengo que cambiar todos los demas

**Back-pressure:**
- Adapter solo transforma mensajes, no puede controlar el flujo
- Mediator puede implementar colas, rate limiting, circuit breakers
- Si un servicio se satura, el Mediator puede pausar o rechazar requests, protegiendo todo el sistema

Basicamente, Adapter es para traducir, Mediator es para orquestar y controlar toda la comunicacion.