# SistemaDeRecomendacion
Sistema de recomendación basado en ítems y usuarios

Si obtenemos un nuevo usuario que califique a 10 artistas, ¿necesitamos ejecutar el algoritmo nuevamente para generar las desviaciones de todos los pares de 200k x 200k o hay alguna forma más fácil?

No es necesario volver a ejecutar el algoritmo en todo el conjunto de datos. Esa es la belleza de este método. Para un par de artículos dado, solo necesitamos hacer un seguimiento de la desviación y el número total de personas que califican ambos artículos.
