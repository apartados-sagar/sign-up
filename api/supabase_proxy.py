from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client

# Conectar con Supabase
supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)

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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Cuando el navegador envía datos (POST)"""
        try:
            # Leer lo que envió el navegador
            tamano = int(self.headers['Content-Length'])
            datos_recibidos = self.rfile.read(tamano)
            datos = json.loads(datos_recibidos)
            
            # Ver qué acción quiere hacer
            accion = datos.get('accion')
            
            # GUARDAR USUARIO
            if accion == 'guardar_usuario':
                resultado = supabase.table('usuarios').insert({
                    'id': datos.get('uid'),
                    'nombre': datos.get('email'),
                    'telefono': datos.get('telefono')
                }).execute()
                
                self.responder({'exito': True, 'datos': resultado.data})
            
            # OBTENER USUARIO
            elif accion == 'obtener_usuario':
                resultado = supabase.table('usuarios').select('*').eq('id', datos.get('uid')).execute()
                self.responder({'exito': True, 'datos': resultado.data})
            
            # Acción no reconocida
            else:
                self.responder({'error': 'No entiendo esa acción'}, codigo=400)
        
        except Exception as error:
            # Si algo salió mal
            self.responder({'error': str(error)}, codigo=500)
    
    def do_GET(self):
        """Cuando el navegador solo pide información (GET)"""
        self.responder({
            'mensaje': 'API funcionando',
            'acciones': ['guardar_usuario', 'obtener_usuario']
        })