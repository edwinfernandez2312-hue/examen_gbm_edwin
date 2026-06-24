--CONSULTA SQL PARA OBTENER TRANSACCIONES APROBADAS CON UN MONTO ACTUAL 5 VECES MAYOR AL ANTERIOR
--uso de cte
WITH transacciones_aprobadas AS (
    SELECT 
        id_cliente,
        id_transaccion,
        fecha_hora,
        monto_usd,
        estado_transaccion,
        --uso de window function
        LAG(monto_usd) OVER (PARTITION BY id_cliente ORDER BY fecha_hora) AS monto_anterior
    FROM transacciones
    --condicion que sea aprobada
    WHERE estado_transaccion = 'aprobada'
)
SELECT 
    id_cliente,
    id_transaccion,
    fecha_hora,
    estado_transaccion,
    monto_anterior,
    monto_usd AS monto_actual
FROM transacciones_aprobadas
--  filtro estricto de las 5 veces
WHERE monto_anterior IS NOT NULL 
  AND monto_usd >= (monto_anterior * 5);