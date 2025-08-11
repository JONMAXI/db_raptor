from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
    'unix_socket': f"/cloudsql/{os.environ.get('DB_CONNECTION_NAME')}"
}

VALID_TOKEN = os.environ.get('VALID_TOKEN')
IMAGEN_URL = "https://maxikash.mx/cdn/shop/files/Cr_dito_Maxikash.png?v=1751590648&width=1950"

# --- Consulta crédito por teléfono ---
@app.route('/consulta_credito', methods=['POST'])
def consulta_credito():
    if not request.content_type or 'application/json' not in request.content_type:
        return jsonify({"estatus": 400, "error": "Content-Type debe ser application/json"}), 400
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {VALID_TOKEN}":
        return jsonify({"estatus": 401, "error": "No autorizado"}), 401

    data = request.get_json(silent=True)
    if not data or 'telefono' not in data:
        return jsonify({"estatus": 400, "error": "Falta telefono en el cuerpo"}), 400

    telefono = data['telefono']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT nombre_cliente, gestor, monto, saldo_total_capital,
                   avance_capital, opcion_1, bono_opcion_1,
                   opcion_2, bono_opcion_2, opcion_3, bono_opcion_3,
                   url
            FROM tbl_cuentas_estrategica
            WHERE telefono_gestor = %s
        """, (telefono,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({"estatus": 404, "error": "Teléfono no encontrado"}), 404

        if not result.get("url"):
            result["url"] = IMAGEN_URL

        return jsonify({"estatus": 200, "data": result}), 200

    except Error as e:
        return jsonify({"estatus": 500, "error": "Error en la base de datos", "detalle": str(e)}), 500

# --- Actualiza respuesta ---
@app.route('/actualiza_respuesta', methods=['POST'])
def actualiza_respuesta():
    if not request.content_type or 'application/json' not in request.content_type:
        return jsonify({"estatus": 400, "error": "Content-Type debe ser application/json"}), 400
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {VALID_TOKEN}":
        return jsonify({"estatus": 401, "error": "No autorizado"}), 401

    data = request.get_json(silent=True)
    if not data or 'telefono' not in data or 'respuesta' not in data:
        return jsonify({"estatus": 400, "error": "Faltan telefono o respuesta en el cuerpo"}), 400

    telefono = data['telefono']
    respuesta = data['respuesta']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tbl_cuentas_estrategica
            SET respuesta = %s
            WHERE telefono_gestor = %s
        """, (respuesta, telefono))
        conn.commit()
        filas_afectadas = cursor.rowcount
        cursor.close()
        conn.close()

        if filas_afectadas == 0:
            return jsonify({"estatus": 404, "error": "Teléfono no encontrado"}), 404

        return jsonify({"estatus": 200, "mensaje": f"Respuesta actualizada correctamente para {telefono}"}), 200

    except Error as e:
        return jsonify({"estatus": 500, "error": "Error en la base de datos", "detalle": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "estatus": 200,
        "mensaje": "Servicio activo. Usa POST /consulta_credito o /actualiza_respuesta con JSON."
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
