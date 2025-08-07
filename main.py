from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

db_config = {
    'host': '34.9.147.5',
    'user': 'jonathan',
    'password': ')1>SbilQ,$VKr=hO',
    'database': 'db_raptor',
    'port': 3306
}

VALID_TOKEN = "PWOYmGdUIMglEdhBZi0yuPXTADI5TeYoRCrJPB7QcmQMElkWMYsJhkKD2EUPUCFZ"

@app.route('/consulta_credito', methods=['POST'])
def consulta_credito():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {VALID_TOKEN}":
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    if not data or 'id_credito' not in data:
        return jsonify({"error": "Falta id_credito en el cuerpo"}), 400

    id_credito = data['id_credito']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM tbl_cuentas_estrategica WHERE id_credito = %s", (id_credito,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({"error": "Crédito no encontrado"}), 404
        
        result.pop('id', None)

        return jsonify({"data": result}), 200

    except Error as e:
        return jsonify({"error": "Error en la base de datos", "detalle": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
