import { auth } from "../../variables.js";
import {create_url} from "../Solicitudes_admin/create_url_image.js"; 
import { signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

function btn_cerrar_modal() {
    signOut(auth).then(() => {
    console.log("Sesión cerrada");
    window.location.href = "/inicio.html";
    document.getElementById('panel-admin').style.display = 'none';
    return;
    }).catch((error) => {
    console.log("Error al cerrar sesión:", error);
    });
}

document.getElementById('btn_cerrar').addEventListener('click', btn_cerrar_modal);


async function subirPlantilla() {
    const user = auth.currentUser;
    
    // Verificar autenticacion
    if (!user) {
        alert('iniciar sesion');
        document.location.href = 'index.html';
    }

    const ADMINS = ['admin@apartadossagar.com'];
  
    if (!ADMINS.includes(user.email)) {
        alert('permiso no autorizado');
        return;
    }

    try {

        const select_area = document.getElementById('select_area').value;
        const select_genero = document.getElementById('select_genero').value;
        const file_image = document.getElementById('file_image').files[0];
        const text_descripcion = document.getElementById('text_descripcion').value;
        const password_base = prompt('Ingrese la contraseña de autorizacion');
        const nombre = file_image.name;

        if (!file_image || !file_image.type.startsWith('image/')) {
            alert('Por favor selecciona un archivo de imagen válido.');
            return;
        }
        
        const url_image = create_url(select_area, select_genero, nombre); // Genera la ruta relativa al bucket

        const formData = new FormData();

        formData.append("accion", "insertar_plantilla");
        formData.append("select_area", select_area);
        formData.append("select_genero", select_genero);
        formData.append("url_image", url_image);
        formData.append("text_descripcion", text_descripcion);
        formData.append("contraseña", password_base);
        formData.append("imagen", file_image);

        const response = await fetch('/api/subir_plantillas',{
            method: 'POST',
            body: formData
        });

        // 1. Verificar si la respuesta fue exitosa
        if (!response.ok) {
            console.error("Error en la respuesta:", response.status);
            return;
        }

        // 2. Convertir la respuesta a JSON
        const data = await response.json();

        // 3. Usar los datos que te devolvió el backend
        console.log("Respuesta del backend:", data);

        const imagenURL = data.imagen_url;       // URL pública de la imagen del backend
        const descripcion = data.descripcion; // Descripción del backend

        // 4. Mostrar la imagen y descripción en tu HTML
        const div_camisas_hombre = document.getElementById('div_c_h');
        div_camisas_hombre.style.backgroundImage = `url('${imagenURL}')`;
        div_camisas_hombre.innerHTML = `<p>${descripcion}</p>`;

        
        alert('Plantilla:', data)
    } catch (error) {
        console.log('Error no se envio:', error);
    }
}

document.getElementById('btnSubir').addEventListener('click',subirPlantilla);