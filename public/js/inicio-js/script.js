function acceder_perfil(){
    window.location.href = '/perfil';
}
export function btn_cerrar_modal() {
    
}
export function btn_enviar_plantilla() {
    
}

window.subirPlantilla = async function(archivo) {
        // Verificar primero si es admin
        const user = auth.currentUser;
        
        if (!user) {
            alert('Debes iniciar sesión');
            return;
        }
        
        if (!ADMINS.includes(user.email)) {
            alert('⛔ No tienes permisos de administrador');
            console.error('Intento de acceso no autorizado');
            return; // ← BLOQUEA la ejecución
        }
        
        // Solo si es admin, continúa
        try {
            const token = await user.getIdToken();
            
            const response = await fetch('/api/subir_plantilla', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ archivo })
            });
            
            const data = await response.json();
            console.log('Plantilla subida:', data);
            
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Otra función de admin
    window.editarPlantilla = async function(id, datos) {
        const user = auth.currentUser;
        
        // Verificar admin SIEMPRE
        if (!user || !ADMINS.includes(user.email)) {
            alert('⛔ No autorizado');
            return;
        }
        
        // Código para editar...
    }