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
            SELECT id_credito, nombre_cliente, gestor, monto, saldo_capital,
                   avance_capital, opciones, bono
            FROM tbl_cuentas_estrategica
            WHERE telefono = %s
        """, (telefono,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({"estatus": 404, "error": "Teléfono no encontrado"}), 404

        return jsonify({"estatus": 200, "data": result}), 200

    except Error as e:
        return jsonify({"estatus": 500, "error": "Error en la base de datos", "detalle": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"estatus": 200, "mensaje": "Servicio activo. Usa POST /consulta_credito con JSON para consultar por teléfono."}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
