
import os
import sqlite3
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "reserva_hotel.db")  

app = Flask(
    __name__,
    template_folder=os.path.join(APP_DIR, "templates"),
    static_folder=os.path.join(APP_DIR, "static")
)

app.secret_key = "cambia-esto-por-una-clave-segura-larga"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_auth():
    """Crea tabla de usuarios y siembra admin si no existe."""
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
          id_usuario    INTEGER PRIMARY KEY AUTOINCREMENT,
          username      TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          rol           TEXT NOT NULL CHECK (rol IN ('admin','usuario')),
          creado_en     TEXT DEFAULT (datetime('now'))
        )
        """)
        row = db.execute("SELECT 1 FROM Usuario WHERE username='admin'").fetchone()
        if not row:
            db.execute(
                "INSERT INTO Usuario (username, password_hash, rol) VALUES (?,?,?)",
                ("admin", generate_password_hash("admin123"), "admin")
            )
        db.commit()


with app.app_context():
    init_auth()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Debes iniciar sesión.", "warning")
                return redirect(url_for("login", next=request.path))
            if session.get("rol") not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.get("/login")
def login():
    
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html", title="Iniciar sesión")


@app.post("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("login"))


@app.post("/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    with get_db() as db:
        u = db.execute(
            "SELECT id_usuario, username, password_hash, rol FROM Usuario WHERE username=?",
            (username,)
        ).fetchone()

    ok = False
    if u:
        
        try:
            ok = check_password_hash(u["password_hash"], password)
        except Exception:
            
            ok = (u["password_hash"] == password)

    if not u or not ok:
        flash("Credenciales inválidas.", "danger")
        return redirect(url_for("login"))

    # sesión
    session["user_id"] = u["id_usuario"]
    session["username"] = u["username"]
    session["rol"] = u["rol"]
    flash(f"Bienvenido, {u['username']} ({u['rol']}).", "success")

    go = request.args.get("next") or url_for("home")
    return redirect(go)




@app.get("/register")
def register():
    
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("register.html", title="Crear cuenta")


@app.post("/register")
def register_post():
    if "user_id" in session:
        return redirect(url_for("home"))

    username  = request.form.get("username", "").strip()
    password  = request.form.get("password", "").strip()
    password2 = request.form.get("password2", "").strip()

    nombre   = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    rut      = request.form.get("rut", "").strip()
    telefono = request.form.get("telefono", "").strip()
    email    = request.form.get("email", "").strip()

   
    if not username or not password:
        flash("Usuario y contraseña son obligatorios.", "danger")
        return redirect(url_for("register"))

    if password != password2:
        flash("Las contraseñas no coinciden.", "danger")
        return redirect(url_for("register"))

    if len(username) < 3:
        flash("El usuario debe tener al menos 3 caracteres.", "warning")
        return redirect(url_for("register"))

    if not nombre or not apellido or not rut:
        flash("Nombre, apellido y RUT son obligatorios.", "danger")
        return redirect(url_for("register"))

    with get_db() as db:
        
        exists = db.execute(
            "SELECT 1 FROM Usuario WHERE username=?",
            (username,)
        ).fetchone()
        if exists:
            flash("Ese nombre de usuario ya está en uso.", "danger")
            return redirect(url_for("register"))

        
        cur = db.execute("""
            INSERT INTO Usuario (username, password_hash, rol)
            VALUES (?, ?, 'usuario')
        """, (username, generate_password_hash(password)))
        user_id = cur.lastrowid

        
        db.execute("""
            INSERT INTO Cliente (nombre, apellido, rut, telefono, email, id_usuario)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, apellido, rut, telefono, email, user_id))

        db.commit()

    flash("Cuenta creada correctamente. Ahora puedes iniciar sesión.", "success")
    return redirect(url_for("login"))


@app.get("/")
@login_required
def home():
    return render_template("home.html", title="Inicio")


@app.get("/clientes")
@roles_required("admin")
def clientes_listar():
    q = request.args.get("q", "").strip()
    with get_db() as db:
        rows = db.execute("""
            SELECT id_cliente, nombre, apellido, rut, telefono, email
            FROM Cliente
            WHERE (? = '' OR nombre LIKE '%'||?||'%' OR apellido LIKE '%'||?||'%'
                   OR rut LIKE '%'||?||'%' OR email LIKE '%'||?||'%')
            ORDER BY id_cliente DESC
        """, (q, q, q, q, q)).fetchall()
    return render_template("clientes.html", rows=rows, q=q, title="Clientes")


@app.post("/clientes")
@roles_required("admin")
def clientes_crear():
    nombre   = request.form.get("nombre","").strip()
    apellido = request.form.get("apellido","").strip()
    rut      = request.form.get("rut","").strip()
    telefono = request.form.get("telefono","").strip()
    email    = request.form.get("email","").strip()

    try:
        with get_db() as db:
            db.execute("""INSERT INTO Cliente (nombre,apellido,rut,telefono,email)
                          VALUES (?,?,?,?,?)""", (nombre,apellido,rut,telefono,email))
            db.commit()
        flash("Cliente creado ✅", "success")
    except Exception as e:
        flash(f"Error creando cliente: {e}", "danger")
    return redirect(url_for("clientes_listar"))


@app.post("/clientes/<int:cid>/borrar")
@roles_required("admin")
def clientes_borrar(cid):
    with get_db() as db:
        cur = db.execute("""
            DELETE FROM Cliente
            WHERE id_cliente=?
              AND NOT EXISTS (
                SELECT 1 FROM Reserva
                WHERE id_cliente=? AND estado IN ('Pendiente','Confirmada')
              )
        """, (cid, cid))
        db.commit()

    if cur.rowcount == 0:
        flash("No se pudo borrar: tiene reservas activas o no existe.", "warning")
    else:
        flash("Cliente borrado ✅", "info")
    return redirect(url_for("clientes_listar"))


@app.get("/disponibilidad")
@login_required
def disponibilidad():
    return render_template("disponibilidad.html", libres=None, title="Disponibilidad")


@app.post("/disponibilidad")
@login_required
def disponibilidad_result():
    desde = request.form.get("desde","").strip()
    hasta = request.form.get("hasta","").strip()

    try:
        datetime.strptime(desde, "%Y-%m-%d")
        datetime.strptime(hasta, "%Y-%m-%d")
    except ValueError:
        flash("Formato de fecha inválido. Use YYYY-MM-DD.", "danger")
        return redirect(url_for("disponibilidad"))

    with get_db() as db:
        libres = db.execute("""
            SELECT H.id_habitacion, H.numero, T.nombre AS tipo, T.precio_noche
            FROM Habitacion H
            JOIN TipoHabitacion T ON T.id_tipo = H.id_tipo
            WHERE H.estado <> 'Mantenimiento'
              AND NOT EXISTS (
                SELECT 1
                FROM Reserva R
                WHERE R.id_habitacion = H.id_habitacion
                  AND R.estado IN ('Pendiente','Confirmada')
                  AND NOT (R.fecha_salida <= ? OR R.fecha_ingreso >= ?)
              )
            ORDER BY T.precio_noche, H.numero
        """, (desde, hasta)).fetchall()

    return render_template(
        "disponibilidad.html",
        libres=libres, desde=desde, hasta=hasta, title="Disponibilidad"
    )


@app.get("/reservas")
@login_required
def reservas_listar():
    rol = session.get("rol")
    user_id = session.get("user_id")

    with get_db() as db:
        if rol == "admin":
            reservas = db.execute("""
                SELECT R.id_reserva,
                       C.nombre || ' ' || C.apellido AS cliente,
                       H.numero AS habitacion,
                       R.fecha_ingreso, R.fecha_salida, R.estado
                FROM Reserva R
                JOIN Cliente C ON C.id_cliente = R.id_cliente
                JOIN Habitacion H ON H.id_habitacion = R.id_habitacion
                ORDER BY R.id_reserva DESC
            """).fetchall()
            clientes = db.execute("""
                SELECT id_cliente, nombre||' '||apellido AS nombre
                FROM Cliente ORDER BY 1 DESC
            """).fetchall()
        else:
            cliente = db.execute("""
                SELECT id_cliente, nombre||' '||apellido AS nombre
                FROM Cliente
                WHERE id_usuario = ?
            """, (user_id,)).fetchone()

            if not cliente:
                reservas = []
                clientes = []
                flash("Tu usuario no está asociado a un cliente. Contacta al administrador.", "warning")
            else:
                reservas = db.execute("""
                    SELECT R.id_reserva,
                           C.nombre || ' ' || C.apellido AS cliente,
                           H.numero AS habitacion,
                           R.fecha_ingreso, R.fecha_salida, R.estado
                    FROM Reserva R
                    JOIN Cliente C ON C.id_cliente = R.id_cliente
                    JOIN Habitacion H ON H.id_habitacion = R.id_habitacion
                    WHERE R.id_cliente = ?
                    ORDER BY R.id_reserva DESC
                """, (cliente["id_cliente"],)).fetchall()
                clientes = [cliente]

        habitaciones = db.execute("""
            SELECT H.id_habitacion, H.numero||' ('||T.nombre||')' AS label
            FROM Habitacion H
            JOIN TipoHabitacion T ON T.id_tipo = H.id_tipo
            WHERE H.estado <> 'Mantenimiento'
            ORDER BY H.numero
        """).fetchall()

    return render_template(
        "reservas.html",
        reservas=reservas, clientes=clientes, habitaciones=habitaciones, title="Reservas"
    )


@app.post("/reservas")
@login_required
def reservas_crear():
    rol = session.get("rol")
    user_id = session.get("user_id")

    id_hab = request.form.get("id_habitacion", type=int)
    fi     = request.form.get("fi", "").strip()
    ff     = request.form.get("ff", "").strip()

    try:
        datetime.strptime(fi, "%Y-%m-%d")
        datetime.strptime(ff, "%Y-%m-%d")
    except ValueError:
        flash("Fechas inválidas.", "danger")
        return redirect(url_for("reservas_listar"))

    with get_db() as db:
        if rol == "admin":
            id_cliente = request.form.get("id_cliente", type=int)
        else:
            cli = db.execute(
                "SELECT id_cliente FROM Cliente WHERE id_usuario = ?",
                (user_id,)
            ).fetchone()
            if not cli:
                flash("Tu usuario no está asociado a un cliente. Contacta al administrador.", "danger")
                return redirect(url_for("reservas_listar"))
            id_cliente = cli["id_cliente"]

        cur = db.execute("""
            INSERT INTO Reserva (id_cliente, id_habitacion, fecha_ingreso, fecha_salida, estado, id_empleado)
            SELECT ?, ?, ?, ?, 'Pendiente', NULL
            WHERE NOT EXISTS (
              SELECT 1 FROM Reserva r
              WHERE r.id_habitacion = ?
                AND r.estado IN ('Pendiente','Confirmada')
                AND NOT (r.fecha_salida <= ? OR r.fecha_ingreso >= ?)
            )
        """, (id_cliente, id_hab, fi, ff, id_hab, fi, ff))
        db.commit()

    flash("Reserva creada (Pendiente) ✅" if cur.rowcount else "No disponible: choque de fechas.", "warning")
    return redirect(url_for("reservas_listar"))


@app.post("/reservas/<int:rid>/estado")
@login_required
def reservas_estado(rid):
    nuevo = request.form.get("estado")
    if nuevo not in ("Confirmada", "Cancelada"):
        flash("Estado inválido.", "danger")
        return redirect(url_for("reservas_listar"))

    rol = session.get("rol")
    user_id = session.get("user_id")

    with get_db() as db:
        if rol == "admin":
            cur = db.execute(
                "UPDATE Reserva SET estado=? WHERE id_reserva=?",
                (nuevo, rid)
            )
        else:
            
            if nuevo != "Cancelada":
                abort(403)

            cli = db.execute(
                "SELECT id_cliente FROM Cliente WHERE id_usuario = ?",
                (user_id,)
            ).fetchone()
            if not cli:
                abort(403)

            cur = db.execute("""
                UPDATE Reserva
                SET estado='Cancelada'
                WHERE id_reserva=? AND id_cliente=?
            """, (rid, cli["id_cliente"]))
        db.commit()

    flash("Estado actualizado ✅" if cur.rowcount else "No se pudo actualizar la reserva.", "info")
    return redirect(url_for("reservas_listar"))


@app.post("/reservas/<int:rid>/reprogramar")
@login_required
def reservas_reprogramar(rid):
    fi = request.form.get("fi","").strip()
    ff = request.form.get("ff","").strip()

    try:
        datetime.strptime(fi, "%Y-%m-%d")
        datetime.strptime(ff, "%Y-%m-%d")
    except ValueError:
        flash("Fechas inválidas.", "danger")
        return redirect(url_for("reservas_listar"))

    rol = session.get("rol")
    user_id = session.get("user_id")

    with get_db() as db:
        if rol == "admin":
            cur = db.execute("""
                UPDATE Reserva
                SET fecha_ingreso=?, fecha_salida=?
                WHERE id_reserva=?
                  AND NOT EXISTS (
                    SELECT 1 FROM Reserva r
                    WHERE r.id_habitacion = (SELECT id_habitacion FROM Reserva WHERE id_reserva=?)
                      AND r.id_reserva <> ?
                      AND r.estado IN ('Pendiente','Confirmada')
                      AND NOT (r.fecha_salida <= ? OR r.fecha_ingreso >= ?)
                  )
            """, (fi, ff, rid, rid, rid, fi, ff))
        else:
            cli = db.execute(
                "SELECT id_cliente FROM Cliente WHERE id_usuario = ?",
                (user_id,)
            ).fetchone()
            if not cli:
                abort(403)

            cur = db.execute("""
                UPDATE Reserva
                SET fecha_ingreso=?, fecha_salida=?
                WHERE id_reserva=?
                  AND id_cliente=?
                  AND NOT EXISTS (
                    SELECT 1 FROM Reserva r
                    WHERE r.id_habitacion = (SELECT id_habitacion FROM Reserva WHERE id_reserva=?)
                      AND r.id_reserva <> ?
                      AND r.estado IN ('Pendiente','Confirmada')
                      AND NOT (r.fecha_salida <= ? OR r.fecha_ingreso >= ?)
                  )
            """, (fi, ff, rid, cli["id_cliente"], rid, rid, fi, ff))
        db.commit()

    flash("Reserva reprogramada ✅" if cur.rowcount else "No se pudo reprogramar (choque, sin permisos o inexistente).", "warning")
    return redirect(url_for("reservas_listar"))


@app.post("/reservas/<int:rid>/eliminar")
@login_required
def reservas_eliminar(rid):
    """
    Eliminar reserva:
      - Debe estar en estado 'Cancelada'.
      - Admin puede borrar cualquier reserva cancelada.
      - Usuario normal solo puede borrar SUS reservas canceladas.
      - Primero se eliminan pagos asociados para no romper la FK.
    """
    rol = session.get("rol")
    user_id = session.get("user_id")

    with get_db() as db:
        if rol == "admin":
            
            db.execute("DELETE FROM Pago WHERE id_reserva = ?", (rid,))
            
            cur = db.execute(
                "DELETE FROM Reserva WHERE id_reserva = ? AND estado = 'Cancelada'",
                (rid,)
            )
        else:
            
            cli = db.execute(
                "SELECT id_cliente FROM Cliente WHERE id_usuario = ?",
                (user_id,)
            ).fetchone()
            if not cli:
                abort(403)

            
            db.execute("""
                DELETE FROM Pago
                WHERE id_reserva IN (
                  SELECT id_reserva FROM Reserva
                  WHERE id_reserva = ? AND id_cliente = ? AND estado = 'Cancelada'
                )
            """, (rid, cli["id_cliente"]))

            
            cur = db.execute("""
                DELETE FROM Reserva
                WHERE id_reserva = ? AND id_cliente = ? AND estado = 'Cancelada'
            """, (rid, cli["id_cliente"]))

        db.commit()

    flash(
        "Reserva eliminada ✅" if cur.rowcount else "Solo puedes eliminar reservas canceladas (y que sean tuyas).",
        "info"
    )
    return redirect(url_for("reservas_listar"))


@app.errorhandler(403)
def forbidden(_e):
    return (
        render_template("base.html", title="Acceso denegado")
        + "<div class='container'><p class='flash danger'>Acceso denegado (403).</p></div>",
        403,
    )


if __name__ == "__main__":
    app.run(debug=True)
