from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client
import cgi


# Conectar con Supabase
supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)

BUCKET_CAMISAS = 'camisas'
BUCKET_PANTALONES = 'pantalones'
BUCKET_JOYERIA = 'joyeria'
BUCKET_PERFUMERIA = 'perfumeria'

GENERO_HOMBRES = 'hombres/'
GENERO_MUJERES = 'mujeres/'

BUCKET_NAME = ''
FILE_PATH = ''

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

    # En el storeg de supabase es cubo/genero/nombrede imagen producto
    # buscar el cubo o area
    def buscar_cubo(select_area):
        match select_area:
            case 'c_':
                # Nombre de cubo camisas
                BUCKET_NAME = BUCKET_CAMISAS
                return BUCKET_NAME 
            case 'p_':
                # Nombre de cubo pantalones
                BUCKET_NAME = BUCKET_PANTALONES
                return BUCKET_NAME 
            case 'j_':
                # Nombre de cubo joyeria
                BUCKET_NAME = BUCKET_JOYERIA
                return BUCKET_NAME
            case 'pr_':
                # Nombre de cubo perfumeria
                BUCKET_NAME = BUCKET_PERFUMERIA
                return BUCKET_NAME
            case _:
                return "Opción no válida"
    # buscar el genero
    def buscar_genero(select_genero):
        match select_genero:
            case 'h':
                FILE_PATH = BUCKET_CAMISAS
                return FILE_PATH
            case 'm':
                FILE_PATH = BUCKET_PANTALONES
                return FILE_PATH
            case _:
                return "Opción no válida"
    
    def do_POST(self):
        """Cuando el navegador envía datos (POST)"""
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            validar = form.getvalue("accion")
            password = form.getvalue("contraseña")
            select_area = form.getvalue("select_area")
            select_genero = form.getvalue("select_genero")
            url_image = form.getvalue("url_image")
            descripcion = form.getvalue("text_descripcion")
            imagen = form.getvalue("imagen")


            # Autorizar el administrador
            response = supabase.auth.sign_in_with_password({
                "email": "admin@apartadossagar.com",
                "password": password
            })
            # verificar el administrador
            if response:
                # Ver qué acción quiere hacer
                accion = validar
            else:
                self.responder({'error': 'No esta autorizado'}, codigo=500)
                return

            # Obtener el id de las imagenes 
            id_imagenes = supabase.table('imagenes').select(
                'id_camisas'
            ).execute()
            
            ultimo_id = id_imagenes.data[-1]['id_camisas'] 
            if ultimo_id == 0:
                nuevo_id = ultimo_id + 1
            else:
                nuevo_id = 1

            # Obtener el cubo preciso
            BUCKET_NAME = self.buscar_cubo(select_area)

            # Accion insertar la plantilla la base de datos
            if accion == 'insertar_plantilla':
                plantilla = supabase.table('imagenes').insert({
                    'id_camisas': nuevo_id,
                    'select_area': select_area,
                    'cubo': BUCKET_NAME,
                    'select_genero': select_genero, # url_image y las demas son nombres de las tablas
                    'descripcion': descripcion,
                    'url_image': url_image
                }).execute()

                ruta_image = supabase.table('imagenes').select({
                    'url_image'
                }).execute()

                descripcion_enviar = supabase.table('imagenes').select({
                    'url_image'
                }).execute()

                file_data = imagen.file.read()

                # insertar la imagen al almacenamiento de archivos de supabase
                res = supabase.storage.from_(BUCKET_NAME).upload(
                    ruta_image,
                    file_data,
                    {"content-type": "image/"}  # Cambia según el tipo de imagen
                )

                # obtener la imagen 
                imagen = supabase.storage.from_(BUCKET_NAME).download(url_image) 

                self.responder({'exito': True,'descripcion': descripcion_enviar, 'imagen': imagen, 'se subio?:': res, 'registro_base': plantilla}) # luego lo quito
            else:
                self.responder({'error': 'accion co comprendida'}, codigo=500)

        except Exception as error:
            # Si algo salió mal
            self.responder({'error': str(error)}, codigo=500)
    
    def do_GET(self):
        """Cuando el navegador solo pide información (GET)"""

        self.responder({
            'mensaje': 'API funcionando',
            'acciones': ['guardar_usuario', 'obtener_plantilla', 'insertar_plantilla']
        })
        

