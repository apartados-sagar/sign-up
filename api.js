// api.js
class API {
    static async request(endpoint, options = {}) {
        const url = `${CONFIG.API_URL}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                'X-API-KEY': CONFIG.API_KEY,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error en API:', error);
            throw error;
        }
    }
    
    // GET
    static async obtenerCamisas() {
        return await this.request('/api/camisas', {
            method: 'GET'
        });
    }
    
    // POST con JSON
    static async crearCamisa(descripcion, imagenUrl) {
        return await this.request('/api/camisas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                descripcion: descripcion,
                imagen_url: imagenUrl
            })
        });
    }
    
    // POST con FormData (subir imagen)
    static async subirImagen(archivo) {
        const formData = new FormData();
        formData.append('imagen', archivo);
        
        return await this.request('/api/subir-imagen', {
            method: 'POST',
            // NO incluir Content-Type, FormData lo hace automático
            body: formData
        });
    }
    
    // PUT
    static async actualizarCamisa(id, descripcion) {
        return await this.request(`/api/camisas/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ descripcion })
        });
    }
    
    // DELETE
    static async eliminarCamisa(id) {
        return await this.request(`/api/camisas/${id}`, {
            method: 'DELETE'
        });
    }
}
