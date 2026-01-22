from http.server import BaseHTTPRequestHandler
import json
import os
import tempfile # Importamos tempfile
from supabase import create_client
import cgi
from typing import cast, IO, Any

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_CAMISAS = 'camisas'
BUCKET_PANTALONES = 'pantalones'
BUCKET_JOYERIA = 'joyeria'
BUCKET_PERFUMERIA = 'perfumeria'

GENERO_HOMBRES = 'hombres/'
GENERO_MUJERES = 'mujeres/'

class handler(BaseHTTPRequestHandler):
    
    def responder(self, datos, codigo=200):
        """
        Función simplificada para responder
        datos: Lo que quieres enviar de vuelta
        codigo: 200 = todo bien, 500 = error
        """
        # Preparar la respuesta
        self.send_response(codigo)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Permitir desde cualquier sitio
        self.end_headers()
        
        # Enviar los datos como JSON
        self.wfile.write(json.dumps(datos).encode())
    
    def do_OPTIONS(self):
        """El navegador pregunta: ¿puedo usar tu API?"""
        self.send_response(200)  # Responder: Sí, puedes
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # En el storage de supabase es cubo/genero/nombrede imagen producto
    # buscar el cubo o area
    def buscar_cubo(self, select_area):
        match select_area:
            case 'c_':
                return BUCKET_CAMISAS
            case 'p_':
                return BUCKET_PANTALONES
            case 'j_':
                return BUCKET_JOYERIA
            case 'pr_':
                return BUCKET_PERFUMERIA
            case _:
                return None
    
    # buscar el genero
    def buscar_genero(self, select_genero):
        match select_genero:
            case 'h':
                return GENERO_HOMBRES
            case 'm':
                return GENERO_MUJERES
            case _:
                return None
    
    def do_POST(self):
        """Cuando el navegador envía datos (POST)"""
        try:

            form = cgi.FieldStorage(
                fp=cast(IO[Any], self.rfile),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Validar que todos los campos requeridos estén presentes
            accion = form.getvalue("accion")
            password = form.getvalue("contraseña")
            select_area = form.getvalue("select_area")
            select_genero = form.getvalue("select_genero")
            url_image = form.getvalue("url_image")
            descripcion = form.getvalue("text_descripcion")

            if not all([accion, password, select_area, select_genero, url_image, descripcion]):
                self.responder({'error': 'Faltan campos requeridos'}, codigo=400)
                return

            # Obtener el archivo de imagen
            if 'imagen' not in form:
                self.responder({'error': 'No se proporcionó archivo de imagen'}, codigo=400)
                return
            
            imagen_file = form['imagen']
            if not imagen_file.filename:
                self.responder({'error': 'Archivo de imagen inválido'}, codigo=400)
                return

            # Validar tipo de archivo
            filename = imagen_file.filename.lower()
            if not (filename.endswith('.jpg') or filename.endswith('.jpeg') or 
                    filename.endswith('.png') or filename.endswith('.webp')):
                self.responder({'error': 'Tipo de archivo no permitido. Use JPG, PNG o WEBP'}, codigo=400)
                return

            # Leer el contenido del archivo
            file_data = imagen_file.file.read()
            if len(file_data) == 0:
                self.responder({'error': 'El archivo está vacío'}, codigo=400)
                return

            # Determinar content-type basado en la extensión
            if filename.endswith('.png'):
                content_type = 'image/png'
            elif filename.endswith('.webp'):
                content_type = 'image/webp'
            else:
                content_type = 'image/jpeg'

            # Autorizar el administrador
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": "admin@apartadossagar.com",
                    "password": password
                })
                if not response or not response.user:
                    self.responder({'error': 'No está autorizado'}, codigo=401)
                    return
            except Exception as auth_error:
                self.responder({'error': 'Error de autenticación'}, codigo=401)
                return

            # Obtener el cubo preciso
            bucket_name = self.buscar_cubo(select_area)
            if not bucket_name:
                self.responder({'error': 'Área no válida'}, codigo=400)
                return

            # Obtener el género
            genero_path = self.buscar_genero(select_genero)
            if not genero_path:
                self.responder({'error': 'Género no válido'}, codigo=400)
                return

            # Accion insertar la plantilla la base de datos
            if accion == 'insertar_plantilla':
                
                # Insertar registro en la base de datos
                # id_camisas es auto-incrementable, no lo insertamos manualmente
                plantilla = supabase.table('imagenes').insert({
                    'select_area': select_area,
                    'cubo': bucket_name,
                    'select_genero': select_genero,
                    'descripcion': descripcion,
                    'url_image': url_image
                }).execute()

                if not plantilla.data or len(plantilla.data) == 0:
                    self.responder({'error': 'Error al insertar en la base de datos'}, codigo=500)
                    return

                # Obtener el ID del registro recién insertado para el rollback
                # Asumiendo que el ID auto-incrementable se devuelve en plantilla.data
                # Si no, deberías obtenerlo de otra manera o reconsiderar cómo manejas los IDs
                

                # Subir la imagen al almacenamiento de Supabase
                try:
                    # La url_image del frontend ya es la ruta relativa dentro del bucket (ej: hombres/header.png)
                    upload_response = supabase.storage.from_(bucket_name).upload(
                        url_image,
                        file_data,
                        {"content-type": content_type, "upsert": "true"}
                    )
                except Exception as upload_error:
                    # Si falla el upload, intentar eliminar el registro de la BD
                    
                    self.responder({'error': f'Error al subir imagen: {str(upload_error)}'}, codigo=500)
                    return


                # Obtener la URL pública de la imagen
                imagen_url_publica = None
                try:
                    # get_public_url devuelve la URL pública directamente
                    public_url_response = supabase.storage.from_(bucket_name).get_public_url(url_image)
                    if public_url_response:
                        imagen_url_publica = public_url_response
                    else:
                        # Construir URL manualmente si el formato no es el esperado
                        imagen_url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{url_image}"
                except Exception as url_error:
                    print(f"Error al obtener URL pública: {url_error}")
                    imagen_url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{url_image}"

                # Responder con datos serializables
                self.responder({
                    'exito': True,
                    'descripcion': descripcion,
                    'imagen_url': imagen_url_publica,
                    'url_image_path_in_bucket': url_image # Para referencia en el frontend
                })

        except Exception as error:
            # Si algo salió mal
            self.responder({'error': f'Error del servidor: {str(error)}'}, codigo=500)
    
    def do_GET(self):
        """Cuando el navegador solo pide información (GET)"""

        self.responder({
            'mensaje': 'API funcionando',
            'acciones': ['guardar_usuario', 'obtener_plantilla', 'insertar_plantilla']
        })
        

