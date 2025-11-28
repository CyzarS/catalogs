import os
from flask import Flask, request, jsonify
from db import get_conn

app = Flask(__name__)

@app.get("/health")
def health():
    return "ok", 200

# CRUD Clientes
@app.get("/clientes")
def listar_clientes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, razon_social, nombre_comercial, rfc, email, telefono FROM clientes ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    clientes = [
        {
            "id": r[0],
            "razon_social": r[1],
            "nombre_comercial": r[2],
            "rfc": r[3],
            "email": r[4],
            "telefono": r[5],
        }
        for r in rows
    ]
    return jsonify(clientes)

@app.get("/clientes/<int:cliente_id>")
def obtener_cliente(cliente_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, razon_social, nombre_comercial, rfc, email, telefono FROM clientes WHERE id=%s", (cliente_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "Cliente no encontrado"}), 404
    cliente = {
        "id": row[0],
        "razon_social": row[1],
        "nombre_comercial": row[2],
        "rfc": row[3],
        "email": row[4],
        "telefono": row[5],
    }
    return jsonify(cliente)

@app.post("/clientes")
def crear_cliente():
    data = request.get_json() or {}
    if "razon_social" not in data or "rfc" not in data:
        return jsonify({"error": "Faltan campos requeridos"}), 400
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clientes (razon_social, nombre_comercial, rfc, email, telefono) VALUES (%s,%s,%s,%s,%s) RETURNING id, razon_social, nombre_comercial, rfc, email, telefono",
        (data.get("razon_social"), data.get("nombre_comercial"), data.get("rfc"), data.get("email"), data.get("telefono")),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    cliente = {
        "id": row[0],
        "razon_social": row[1],
        "nombre_comercial": row[2],
        "rfc": row[3],
        "email": row[4],
        "telefono": row[5],
    }
    return jsonify(cliente), 201

@app.put("/clientes/<int:cliente_id>")
def actualizar_cliente(cliente_id):
    data = request.get_json() or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE clientes SET razon_social=%s, nombre_comercial=%s, rfc=%s, email=%s, telefono=%s WHERE id=%s RETURNING id, razon_social, nombre_comercial, rfc, email, telefono",
        (data.get("razon_social"), data.get("nombre_comercial"), data.get("rfc"), data.get("email"), data.get("telefono"), cliente_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "Cliente no encontrado"}), 404
    cliente = {
        "id": row[0],
        "razon_social": row[1],
        "nombre_comercial": row[2],
        "rfc": row[3],
        "email": row[4],
        "telefono": row[5],
    }
    return jsonify(cliente)

@app.delete("/clientes/<int:cliente_id>")
def eliminar_cliente(cliente_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
    count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if count == 0:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return "", 204

# Los CRUD de domicilios y productos se implementan de manera similar.

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3001"))
    app.run(host="0.0.0.0", port=port)
