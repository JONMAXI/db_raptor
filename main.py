from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os
import uuid
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
from google.cloud import storage
import requests

app = Flask(__name__)

# Configuración BD desde variables de entorno
db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
    'unix_socket': f"/cloudsql/{os.environ.get('DB_CONNECTION_NAME')}"
}

VALID_TOKEN = os.environ.get('VALID_TOKEN')
BUCKET_NAME = "storage_raptor"  # Nombre de tu bucket

def generar_imagen(data):
    # Descargar template
    template_url = "https://ffd31284c1c946b2ea3e1821f67743dcbef34ba1244b298169e61de-apidata.googleusercontent.com/download/storage/v1/b/storage_raptor/o/template.jpeg?jk=AXbWWmlvXUaflqHpporiScIJg6Fb_P36elT6qTIVlOFwSq2FkYEYcgHpKESHgJ9ZtOYEQ6ZstU0w-TC2h4XqImp_UwhIAiLFHdH3DltEg73ETkmHw3O_BU_-kDnoFKSsO1OjCo61_XPYS3aLhaQWFzxbm_420J2iW5HDRFlleajfx5Zt65LvFSRZm9xwB3rKlVyaSbi_6ZL_I97lTmcH4fV4vpQJs2D5W3Ssyr8r5Jmoleup7EQO8Vp-8SzoSQG5exBZafa-_blBfPtTHCXezvmwivrrBLkgkYsvE8RWUFmnwLWXYalj2Os5BY5cTipvH6NCM8PO533UM3dTgQ8bAwop6pejDRgDV8AxIxFaxHzzUuSge4dOhhfE13ES3YkzArOlhnsRewChrKP6tV5Oud-R6yle9JLQRwa2Gq0PbctFbqXbs5uq-yKNd7x5BKLSpU0dfwskWRT9uXyww2BeIAh_5p0be5wQ7dXtmrxd6d0DuazNfTZIQyha2ywhT6MumdFVYcaUIcfrCsM60o59BUKugpS804cK10l-2mKea8VaSS9NQzevByNqjzK3UwpAcG22-sh5wWLEnssD9eDlAA6ejdU77y2nQbFKYPR67uwMCOBLYN_qpSA1YFCvjt9zphz52hQnNskK8KHBbbAfo-6ZXrJ8xtGMYXXDRpcZglRZtTNjkCYjQ4L7ZeV5Ms94qFY1kLdfTea8xIo1-FHkoPOdAXyClf3BEpZIva4xEzsn1G2p2fEXgNFu8RdQ1hMyhzxOLeW7Ki5i4kjFNLyKRF0fnT8b0OTg589fceI6J_bgS_kFDrF7iG5kKT2v3IahCKP3zNdFVr16IVAYjn3VH6AlopghPnTPApHbbv0ctA23gZzPoGsfWKM5UwKq6L6S9AzhuCrsZUTal8-PFvR0mYCiqeH2XK0BtqryWQ50o8FzZEKiGODAU_eApMJjhMP6tsID7FjDLeH9eirFa7XUvcgX-2namDH875_oOoJpioiPT2NGhdSoRUvxoJnK9uzlhWGrRQzWdJeA7LfF2RKIhc17Igx6mPDF9c4FqRm7sLhIgFquT1I-0jF-GzL4gUNWRKwx8KLMnWUmptDcY-1GAV-bYbQClj_kp7kIg_-XbUwmW7nVw2OaVFGdCVSm6MC9v3dU3yU1QQ&isca=1"
    response = requests.get(template_url)
    response.raise_for_status()
    img_base = Image.open(BytesIO(response.content))

    nombre_cliente = data.get('nombre_cliente', '')
    opciones = [data.get('opcion_1', ''), data.get('opcion_2', ''), data.get('opcion_3', '')]
    bonos = [data.get('bono_opcion_1', ''), data.get('bono_opcion_2', ''), data.get('bono_opcion_3', '')]

    draw = ImageDraw.Draw(img_base)

    # Usar fuente por defecto para evitar problemas en el contenedor
    font = ImageFont.load_default()
    font_nombre = ImageFont.load_default()

    text_fill = (0, 0, 0)
    shadow_fill = (180, 180, 180)
    color_cafe = (101, 67, 33)

    x_center = img_base.width // 2
    start_y = 900
    current_y = start_y

    for line in textwrap.wrap(nombre_cliente, width=60):
        bbox = font_nombre.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = x_center - text_width // 2
        draw.text((x + 2, current_y + 2), line, font=font_nombre, fill=shadow_fill)
        draw.text((x, current_y), line, font=font_nombre, fill=text_fill)
        current_y += bbox[3] - bbox[1] + 15

    current_y += 40

    col_opciones_center = img_base.width // 4
    col_bonos_center = (img_base.width * 3) // 4
    draw.text((col_opciones_center - font.getbbox("Opciones")[2] // 2, current_y), "Opciones", font=font, fill=text_fill)
    draw.text((col_bonos_center - font.getbbox("Bonos")[2] // 2, current_y), "Bonos", font=font, fill=text_fill)
    text_height = font.getbbox("Opciones")[3] - font.getbbox("Opciones")[1]
    current_y += text_height + 15

    for opcion, bono in zip(opciones, bonos):
        bbox_opcion = font.getbbox(str(opcion))
        x_opcion = col_opciones_center - (bbox_opcion[2] - bbox_opcion[0]) // 2
        draw.text((x_opcion + 2, current_y + 2), str(opcion), font=font, fill=shadow_fill)
        draw.text((x_opcion, current_y), str(opcion), font=font, fill=color_cafe)

        try:
            bono_num = float(bono)
            bono_text = f"${bono_num:,.2f}"
        except:
            bono_text = str(bono)
        bbox_bono = font.getbbox(bono_text)
        x_bono = col_bonos_center - (bbox_bono[2] - bbox_bono[0]) // 2
        draw.text((x_bono + 2, current_y + 2), bono_text, font=font, fill=shadow_fill)
        draw.text((x_bono, current_y), bono_text, font=font, fill=color_cafe)

        current_y += text_height + 15

    img_bytes = BytesIO()
    img_base.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def subir_a_bucket(file_bytes, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_file(file_bytes, content_type='image/png')
    blob.make_public()
    return blob.public_url

@app.route('/consulta_credito', methods=['POST'])
def consulta_credito():
    if not request.content_type or 'application/json' not in request.content_type:
        return jsonify({"estatus": 400, "error": "Content-Type debe ser application/json"}), 400
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {VALID_TOKEN}":
        return jsonify({"estatus": 401, "error": "No autorizado"}), 401

    data = request.get_json(silent=True)
    if not data or 'telefono' not in data:
        return jsonify({"estatus": 400, "error": "Falta telefono"}), 400

    telefono = data['telefono']
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT nombre_cliente, opcion_1, bono_opcion_1,
                   opcion_2, bono_opcion_2, opcion_3, bono_opcion_3
            FROM tbl_cuentas_estrategica
            WHERE telefono_gestor = %s
        """, (telefono,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({"estatus": 404, "error": "Teléfono no encontrado"}), 404

        img_bytes = generar_imagen(result)
        filename = f"credito_{uuid.uuid4()}.png"
        public_url = subir_a_bucket(img_bytes, filename)
        result['url_imagen'] = public_url

        return jsonify({"estatus": 200, "data": result}), 200

    except Error as e:
        return jsonify({"estatus": 500, "error": str(e)}), 500
    except Exception as e:
        return jsonify({"estatus": 500, "error": f"Error general: {str(e)}"}), 500

@app.route('/')
def home():
    return jsonify({"estatus": 200, "mensaje": "Servicio activo"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
