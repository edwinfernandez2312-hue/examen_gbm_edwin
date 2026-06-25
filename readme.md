 Fase 1: Diseño del Flujo y Toma de Decisiones

 1. Justificación de Calidad de Datos - 

Antes de que los datos sean consumidos por el equipo de analítica avanzada, es indispensable garantizar su calidad y consistencia. Las reglas de negocio definidas permiten reducir errores que podrían afectar la detección de fraude y la toma de decisiones.

Eliminación de registros duplicados

La existencia de transacciones duplicadas genera una representación incorrecta de la actividad financiera de los clientes. Esto puede provocar sobreestimación de montos, falsos positivos en modelos de fraude y métricas analíticas inexactas. Por esta razón, se eliminan los registros duplicados utilizando el identificador único `id_transaccion`.

Tratamiento de valores faltantes

Los valores nulos en la columna `monto_usd` pueden causar errores durante los procesos de análisis y cálculo. Cuando una transacción se encuentra en estado `rechazada`, el monto no representa un movimiento financiero efectivo; por ello, asignar el valor `0.0` permite mantener la consistencia de los datos sin alterar el significado del registro.

 Clasificación de montos inusuales

La creación de la variable booleana `es_monto_inusual` permite identificar de manera temprana transacciones con características potencialmente riesgosas. Se consideran inusuales aquellas transacciones internacionales cuyo monto supera los $1,500 USD, facilitando futuras investigaciones y análisis de fraude.

Exclusión de transacciones no aprobadas

Para el análisis de anomalías de gasto únicamente deben considerarse transacciones aprobadas, ya que representan operaciones efectivamente realizadas por los clientes. Incluir transacciones rechazadas o pendientes podría generar conclusiones erróneas y afectar la precisión del análisis.

---

2. Arquitectura Propuesta


## 2. Arquitectura del Flujo
El flujo sigue un modelo **ETL (Extract, Transform, Load)** robusto:

`CSV (Raw)` ➔ `Pandas (Transform)` ➔ `Supabase (Load)` ➔ `SQL (Analysis)`
"Nota: Por razones de seguridad, las credenciales se gestionan a través de variables de entorno. Se requiere un archivo .env local con SUPABASE_URL y SUPABASE_KEY

3. Gobernanza y Seguridad de Datos (RBAC & RLS)
Para garantizar la integridad y confidencialidad de la información, hemos implementado una capa de seguridad a nivel de base de datos utilizando dos pilares fundamentales: RBAC (Control de Acceso Basado en Roles) y RLS (Row Level Security).

Jerarquía de Acceso (RBAC)
Hemos definido tres niveles de privilegios mediante un tipo de dato enumerado (rol_usuario) vinculado a la autenticación de Supabase:

Administrador: Acceso total a la tabla de transacciones.

Analista Senior: Acceso de lectura total para auditorías y reportes complejos.

Analista Junior: Acceso restringido únicamente a transacciones con estado 'aprobada'.

Seguridad a Nivel de Fila (RLS)
La seguridad no depende de la aplicación, sino del motor de base de datos. Se han habilitado políticas (Policies) en PostgreSQL que actúan como un filtro dinámico:

Al realizar una consulta, la base de datos verifica el auth.uid() del usuario y su rol en la tabla perfiles_usuarios.

Si el usuario es Junior, el sistema oculta automáticamente todas las filas que no estén aprobadas, sin necesidad de modificar el código SQL de la consulta.

### Tecnologías Utilizadas
* **Python & Pandas:** Procesamiento eficiente y limpieza de datos (Dataframes).
* **Supabase (PostgreSQL):** Base de datos relacional en la nube para almacenamiento estructurado.
* **SQL:** Análisis mediante *Window Functions* y *CTEs* para detección de anomalías.
* **Apache Airflow:** Orquestador para automatización diaria (11:30 PM) y gestión de dependencias.

Python

Se utilizará Python como lenguaje principal debido a su amplia adopción en proyectos de Ingeniería de Datos. Permite automatizar procesos ETL, integrarse fácilmente con bases de datos y manejar grandes volúmenes de información mediante librerías especializadas.

Pandas

Pandas será la librería encargada de la transformación de los datos. Su estructura DataFrame facilita la limpieza, validación y manipulación de registros, permitiendo implementar de forma eficiente las reglas de negocio definidas para el proyecto.

CSV (Formato de Entrada)

El archivo CSV representa la fuente de datos cruda entregada diariamente por el área de negocio. Este formato es ampliamente utilizado por su simplicidad, compatibilidad y facilidad de intercambio entre sistemas.

DataFrame de Pandas (Formato Intermedio)

Después de la extracción, los datos serán almacenados temporalmente en un DataFrame. Este formato intermedio permite aplicar validaciones, eliminar duplicados, tratar valores nulos y generar nuevas columnas antes de persistir la información en la base de datos.


Supabase (PostgreSQL)

Supabase será el destino final de almacenamiento. Al estar basado en PostgreSQL, proporciona un motor relacional robusto, soporte para consultas analíticas complejas, escalabilidad y compatibilidad con estándares SQL ampliamente utilizados en la industria.

SQL

SQL será utilizado para realizar consultas analíticas sobre los datos ya procesados. En particular, se emplearán Common Table Expressions (CTEs) y Window Functions para identificar anomalías de gasto comparando transacciones consecutivas de cada cliente.

Apache Airflow

Apache Airflow se propone como herramienta de orquestación para ambientes productivos. Permitirá programar la ejecución automática del pipeline todos los días a las 11:30 PM, controlar dependencias entre tareas y garantizar que la carga y el análisis solo se ejecuten cuando las transformaciones hayan finalizado correctamente


--------------------------------------------------------------------------------------
Para este MVP (Producto Mínimo Viable), la decisión de trabajar con una tabla única y desnormalizada en lugar de un esquema estrella (Star Schema) se basó en los siguientes criterios técnicos:


Alcance del Requerimiento: El problema de negocio solicitaba explícitamente la carga y análisis sobre una estructura consolidada. Implementar dimensiones (dim_cliente, dim_tiempo) hubiera sido una sobreingeniería innecesaria para el alcance actual.

Eficiencia de Consultas: Al trabajar con una tabla plana, eliminamos la necesidad de realizar múltiples JOINs complejos, lo que reduce la latencia en las consultas analíticas sobre anomalías.

Agilidad en el ETL: Un esquema estrella requiere una lógica de carga mucho más pesada para mantener la integridad referencial entre tablas. Al utilizar una sola tabla, simplificamos la tubería de datos y minimizamos los puntos de fallo.