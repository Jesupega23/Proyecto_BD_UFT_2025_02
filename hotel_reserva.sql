--
-- Archivo generado con SQLiteStudio v3.4.17 el mié. oct. 22 22:21:19 2025
--
-- Codificación de texto usada: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Tabla: Cliente
CREATE TABLE IF NOT EXISTS Cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    apellido    TEXT NOT NULL,
    rut         TEXT UNIQUE NOT NULL,
    telefono    TEXT,
    email       TEXT
);
INSERT INTO Cliente (id_cliente, nombre, apellido, rut, telefono, email) VALUES (1, 'Juan', 'Pérez', '12.345.678-9', '912345678', 'juanperez@gmail.com');
INSERT INTO Cliente (id_cliente, nombre, apellido, rut, telefono, email) VALUES (2, 'María', 'Gómez', '15.678.123-4', '987654321', 'mariagomez@gmail.com');

-- Tabla: Empleado
CREATE TABLE IF NOT EXISTS Empleado (
    id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    apellido    TEXT NOT NULL,
    cargo       TEXT NOT NULL,
    usuario     TEXT UNIQUE NOT NULL,
    contrasena  TEXT NOT NULL
);
INSERT INTO Empleado (id_empleado, nombre, apellido, cargo, usuario, contrasena) VALUES (1, 'Pedro', 'López', 'Recepcionista', 'plopez', '1234');
INSERT INTO Empleado (id_empleado, nombre, apellido, cargo, usuario, contrasena) VALUES (2, 'Ana', 'Rojas', 'Administradora', 'arojas', 'abcd');

-- Tabla: Habitacion
CREATE TABLE IF NOT EXISTS Habitacion (
    id_habitacion INTEGER PRIMARY KEY AUTOINCREMENT,
    numero        TEXT UNIQUE NOT NULL,
    id_tipo       INTEGER NOT NULL,
    estado        TEXT CHECK(estado IN ('Disponible','Ocupada','Mantenimiento')) DEFAULT 'Disponible',
    FOREIGN KEY (id_tipo) REFERENCES TipoHabitacion(id_tipo)
);
INSERT INTO Habitacion (id_habitacion, numero, id_tipo, estado) VALUES (1, '101', 1, 'Disponible');
INSERT INTO Habitacion (id_habitacion, numero, id_tipo, estado) VALUES (2, '102', 1, 'Disponible');
INSERT INTO Habitacion (id_habitacion, numero, id_tipo, estado) VALUES (3, '201', 2, 'Ocupada');
INSERT INTO Habitacion (id_habitacion, numero, id_tipo, estado) VALUES (4, '202', 2, 'Disponible');
INSERT INTO Habitacion (id_habitacion, numero, id_tipo, estado) VALUES (5, '301', 3, 'Mantenimiento');

-- Tabla: Pago
CREATE TABLE IF NOT EXISTS Pago (
    id_pago     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_reserva  INTEGER NOT NULL,
    monto       REAL NOT NULL,
    metodo_pago TEXT CHECK(metodo_pago IN ('Efectivo','Tarjeta','Transferencia')),
    fecha_pago  DATE DEFAULT (DATE('now')),
    FOREIGN KEY (id_reserva) REFERENCES Reserva(id_reserva)
);
INSERT INTO Pago (id_pago, id_reserva, monto, metodo_pago, fecha_pago) VALUES (1, 1, 375000.0, 'Tarjeta', '2025-10-23');

-- Tabla: Reserva
CREATE TABLE IF NOT EXISTS Reserva (
    id_reserva     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente     INTEGER NOT NULL,
    id_habitacion  INTEGER NOT NULL,
    fecha_ingreso  DATE NOT NULL,
    fecha_salida   DATE NOT NULL,
    estado         TEXT CHECK(estado IN ('Pendiente','Confirmada','Cancelada')) DEFAULT 'Pendiente',
    id_empleado    INTEGER,
    FOREIGN KEY (id_cliente)    REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_habitacion) REFERENCES Habitacion(id_habitacion),
    FOREIGN KEY (id_empleado)   REFERENCES Empleado(id_empleado)
);
INSERT INTO Reserva (id_reserva, id_cliente, id_habitacion, fecha_ingreso, fecha_salida, estado, id_empleado) VALUES (1, 1, 3, '2025-10-25', '2025-10-30', 'Confirmada', 1);
INSERT INTO Reserva (id_reserva, id_cliente, id_habitacion, fecha_ingreso, fecha_salida, estado, id_empleado) VALUES (2, 2, 2, '2025-10-28', '2025-10-29', 'Pendiente', 1);

-- Tabla: TipoHabitacion
CREATE TABLE IF NOT EXISTS TipoHabitacion (
    id_tipo       INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    descripcion   TEXT,
    precio_noche  REAL NOT NULL
);
INSERT INTO TipoHabitacion (id_tipo, nombre, descripcion, precio_noche) VALUES (1, 'Individual', 'Cama individual, baño privado', 45000.0);
INSERT INTO TipoHabitacion (id_tipo, nombre, descripcion, precio_noche) VALUES (2, 'Doble', 'Cama doble, vista al mar', 75000.0);
INSERT INTO TipoHabitacion (id_tipo, nombre, descripcion, precio_noche) VALUES (3, 'Suite', 'Suite con jacuzzi y terraza', 120000.0);

-- Índice: idx_reserva_cliente
CREATE INDEX IF NOT EXISTS idx_reserva_cliente    ON Reserva(id_cliente);

-- Índice: idx_reserva_habitacion
CREATE INDEX IF NOT EXISTS idx_reserva_habitacion ON Reserva(id_habitacion);

-- Vista: HabitacionesDisponibles
CREATE VIEW IF NOT EXISTS HabitacionesDisponibles AS
SELECT H.numero,
       T.nombre AS tipo,
       T.precio_noche
FROM Habitacion H
JOIN TipoHabitacion T ON H.id_tipo = T.id_tipo
WHERE H.estado = 'Disponible';

-- Vista: ReservasActivas
CREATE VIEW IF NOT EXISTS ReservasActivas AS
SELECT R.id_reserva,
       C.nombre || ' ' || C.apellido AS cliente,
       H.numero AS habitacion,
       R.fecha_ingreso,
       R.fecha_salida,
       R.estado
FROM Reserva R
JOIN Cliente    C ON R.id_cliente    = C.id_cliente
JOIN Habitacion H ON R.id_habitacion = H.id_habitacion
WHERE R.estado = 'Confirmada';

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
