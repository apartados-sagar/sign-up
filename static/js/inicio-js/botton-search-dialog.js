function search(){
    const dialog = document.getElementById("main-dialog-busqueda");
    const input = document.getElementById("to-search");
    const divImg = document.getElementById("dialog-div-img");
    const btncerrar = document.getElementById("button-dialog-cerrar");

    // Crear los estilos para las imágenes
    divImg.innerHTML = `
    
    `;

    dialog.showModal();
    
}
function btn_cerrar(){
    const dialog = document.getElementById("main-dialog-busqueda");
    dialog.close();
}