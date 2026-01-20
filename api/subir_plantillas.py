from http.server import BaseHTTPRequestHandler
import json
import os
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
                # Obtener el último ID de las imágenes
                try:
                    id_imagenes = supabase.table('imagenes').select('id_camisas').order('id_camisas', desc=True).limit(1).execute()
                    
                    if id_imagenes.data and len(id_imagenes.data) > 0:
                        ultimo_id = id_imagenes.data[0].get('id_camisas', 0)
                        nuevo_id = ultimo_id + 1 if ultimo_id > 0 else 1
                    else:
                        nuevo_id = 1
                except Exception as id_error:
                    # Si hay error al obtener ID, empezar desde 1
                    nuevo_id = 1

                # Insertar registro en la base de datos
                plantilla = supabase.table('imagenes').insert({
                    'id_camisas': nuevo_id,
                    'select_area': select_area,
                    'cubo': bucket_name,
                    'select_genero': select_genero,
                    'descripcion': descripcion,
                    'url_image': url_image
                }).execute()

                if not plantilla.data or len(plantilla.data) == 0:
                    self.responder({'error': 'Error al insertar en la base de datos'}, codigo=500)
                    return

                # Subir la imagen al almacenamiento de Supabase
                try:
                    upload_response = supabase.storage.from_(bucket_name).upload(
                        url_image,
                        file_data,
                        {"content-type": content_type, "upsert": "true"}
                    )
                except Exception as upload_error:
                    # Si falla el upload, intentar eliminar el registro de la BD
                    try:
                        supabase.table('imagenes').delete().eq('id_camisas', nuevo_id).execute()
                    except:
                        pass
                    self.responder({'error': f'Error al subir imagen: {str(upload_error)}'}, codigo=500)
                    return

                # Obtener la URL pública de la imagen
                try:
                    public_url_response = supabase.storage.from_(bucket_name).get_public_url(url_image)
                    # get_public_url puede retornar un string directamente o un objeto con la propiedad 'publicUrl'
                    if isinstance(public_url_response, str):
                        imagen_url_publica = public_url_response
                    elif hasattr(public_url_response, 'publicUrl'):
                        imagen_url_publica = public_url_response.publicUrl
                    else:
                        # Construir URL manualmente si el formato no es el esperado
                        imagen_url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{url_image}"
                except Exception:
                    # Si no se puede obtener URL pública, construirla manualmente
                    imagen_url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{url_image}"

                # Responder con datos serializables
                self.responder({
                    'exito': True,
                    'descripcion': descripcion,
                    'imagen_url': imagen_url_publica,
                    'id_registro': nuevo_id,
                    'url_image': url_image
                })
            else:
                self.responder({'error': 'Acción no comprendida'}, codigo=400)

        except Exception as error:
            # Si algo salió mal
            self.responder({'error': f'Error del servidor: {str(error)}'}, codigo=500)
    
    def do_GET(self):
        """Cuando el navegador solo pide información (GET)"""

        self.responder({
            'mensaje': 'API funcionando',
            'acciones': ['guardar_usuario', 'obtener_plantilla', 'insertar_plantilla']
        })
        

