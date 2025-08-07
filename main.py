from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# Configuración DB desde variables de entorno para Cloud SQL Proxy
db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
    'unix_socket': f"/cloudsql/{os.environ.get('DB_CONNECTION_NAME')}"
}

VALID_TOKEN = os.environ.get('VALID_TOKEN')  # Token también desde variable de entorno

@app.route('/consulta_credito', methods=['POST'])
def consulta_credito():
    # Validar Content-Type JSON
    if not request.content_type or 'application/json' not in request.content_type:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400
    
    # Validar token en header Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {VALID_TOKEN}":
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json(silent=True)
    if not data or 'id_credito' not in data:
        return jsonify({"error": "Falta id_credito en el cuerpo"}), 400

    id_credito = data['id_credito']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id_credito, nombre_cliente, gestor, monto, saldo_capital,
                   avance_capital, opciones, bono, estatus
            FROM tbl_cuentas_estrategica
            WHERE id_credito = %s
        """, (id_credito,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({"error": "Crédito no encontrado"}), 404

        return jsonify({"data": result}), 200

    except Error as e:
        return jsonify({"error": "Error en la base de datos", "detalle": str(e)}), 500

@app.route('/')
def home():
    return "Servicio activo. Usa POST /consulta_credito con JSON para consultar.", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
