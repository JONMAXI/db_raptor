import mysql.connector
from mysql.connector import Error
from flask import jsonify

# Configuración DB y token
db_config = {
    'host': '34.9.147.5',
    'user': 'jonathan',
    'password': ')1>SbilQ,$VKr=hO',
    'database': 'db_raptor',
    'port': 3306
}

VALID_TOKEN = "PWOYmGdUIMglEdhBZi0yuPXTADI5TeYoRCrJPB7QcmQMElkWMYsJhkKD2EUPUCFZ"

def consulta_credito(request):
    # Validar método POST
    if request.method != 'POST':
        return jsonify({"error": "Método no permitido"}), 405
    
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
        
        cursor.execute("SELECT * FROM tbl_cuentas_estrategica WHERE id_credito = %s", (id_credito,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({"error": "Crédito no encontrado"}), 404
        
        result.pop('id', None)  # Remover autoincrement si existe

        return jsonify({"data": result}), 200

    except Error as e:
        return jsonify({"error": "Error en la base de datos", "detalle": str(e)}), 500
