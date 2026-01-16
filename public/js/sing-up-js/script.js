function acceder() {
    const nombre = document.getElementById("nombre").value;
    const telefono = document.getElementById("telefono").value;
    // Guardar usuario
    fetch('/api/supabase_proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            accion: 'guardar_usuario',
            nombre: nombre,
            telefono: telefono
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.exito) {
            console.log('¡Guardado!', data.datos);
        }
    });
}


function autenticaradmin(){
    const dialog = document.getElementById("dialog");

    dialog.showModal();;
}

function Cerrar(){
    const dialog = document.getElementById("dialog");

    dialog.close();
}
