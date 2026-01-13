
// app.js - Ejemplos de uso
async function cargarCamisas() {
    try {
        const data = await API.obtenerCamisas();
        console.log('Camisas:', data);
        mostrarCamisas(data.camisas);
    } catch (error) {
        console.error('Error al cargar camisas:', error);
    }
}

async function subirNuevaCamisa() {
    const fileInput = document.getElementById('fileInput');
    const descripcion = document.getElementById('descripcion').value;
    const archivo = fileInput.files[0];
    
    if (!archivo) {
        alert('Selecciona una imagen');
        return;
    }
    
    try {
        // 1. Subir imagen
        const resultImagen = await API.subirImagen(archivo);
        console.log('Imagen subida:', resultImagen.url);
        
        // 2. Crear registro en base de datos
        const resultCamisa = await API.crearCamisa(descripcion, resultImagen.url);
        console.log('Camisa creada:', resultCamisa);
        
        alert('Camisa agregada exitosamente!');
        cargarCamisas(); // Recargar lista
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al subir camisa');
    }
}

function mostrarCamisas(camisas) {
    const container = document.getElementById('camisasContainer');
    container.innerHTML = '';
    
    camisas.forEach(camisa => {
        container.innerHTML += `
            <div class="camisa">
                <img src="${camisa.imagen_url}" alt="${camisa.descripcion}">
                <p>${camisa.descripcion}</p>
                <button onclick="eliminarCamisa(${camisa.id_camisas})">Eliminar</button>
            </div>
        `;
    });
}

async function eliminarCamisa(id) {
    if (!confirm('¿Eliminar esta camisa?')) return;
    
    try {
        await API.eliminarCamisa(id);
        alert('Camisa eliminada');
        cargarCamisas();
    } catch (error) {
        console.error('Error:', error);
    }
}

// Cargar al inicio
window.onload = () => {
    cargarCamisas();
};