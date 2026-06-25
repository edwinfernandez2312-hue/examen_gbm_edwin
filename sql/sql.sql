--CREACION DE ROLES PARA USUARIO DE SUPABASE

-- 1 ENUM para los roles del equipo
CREATE TYPE rol_usuario AS ENUM ('analista_junior', 'analista_senior', 'administrador');

-- 2. tabla de perfiles vinculada a la autenticación nativa de Supabase
CREATE TABLE IF NOT EXISTS perfiles_usuarios (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    correo TEXT NOT NULL,
    rol rol_usuario DEFAULT 'analista_junior'::rol_usuario,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Habilitar la seguridad a nivel de fila (RLS) en tu tabla principal
ALTER TABLE transacciones ENABLE ROW LEVEL SECURITY;

-- 4. POLÍTICA 1: Administradores y Senior pueden ver y modificar TODAS las transacciones
CREATE POLICY "Acceso total para Senior y Admin" 
ON transacciones
FOR ALL 
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM perfiles_usuarios 
        WHERE perfiles_usuarios.id = auth.uid() 
        AND perfiles_usuarios.rol IN ('analista_senior'::rol_usuario, 'administrador'::rol_usuario)
    )
);

-- 5. POLÍTICA 2: Analistas Junior SOLO pueden leer las transacciones que estén 'aprobadas'
CREATE POLICY "Lectura restringida para Junior" 
ON transacciones
FOR SELECT 
TO authenticated
USING (
    estado_transaccion = 'aprobada'
    AND EXISTS (
        SELECT 1 FROM perfiles_usuarios 
        WHERE perfiles_usuarios.id = auth.uid() 
        AND perfiles_usuarios.rol = 'analista_junior'::rol_usuario
    )
);




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