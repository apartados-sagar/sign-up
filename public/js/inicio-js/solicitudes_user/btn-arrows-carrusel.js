/* Area de Camisas............................*/
/* flechas hombres...................*/
/* c_h camisas hombres ....*/
let currentIndex = 0;
const track = document.getElementById('slider-track');
const plantillas = document.querySelectorAll('.plantilla');
const totalPlantillas = plantillas.length;

function P_H_arrow_right() {
    if (currentIndex < totalPlantillas - 1) {
        currentIndex++;
    } else {
        currentIndex = 0; // Volver al inicio
    }
    actualizarSlider();
}

function P_H_arrow_left() {
    if (currentIndex > 0) {
        currentIndex--;
    } else {
        currentIndex = totalPlantillas - 1; // Ir al final
    }
    actualizarSlider()
}
function actualizarSlider() {
    const desplazamiento = -currentIndex * 100;
    track.style.transform = `translateX(${desplazamiento}%)`;
}

function C_H_arrow_left(){
     
}
function C_H_arrow_right(){

}
/* flechas Mujeres...................*/
function C_M_arrow_left(){

}
function C_M_arrow_right(){

}
/* Area de Pantalones............................*/
/* flechas hombres...................*/
function P_H_arrow_left(){

}
function P_H_arrow_right(){

}
/* flechas Mujeres...................*/
function C_M_arrow_left(){

}
function C_M_arrow_right(){

}
/* Area de joyeria............................*/
/* flechas hombres...................*/
function J_H_arrow_left(){

}
function J_H_arrow_right(){

}
/* flechas Mujeres...................*/
function J_M_arrow_left(){

}
function J_M_arrow_right(){

}
/* Area de perfumeria............................*/
/* flechas hombres...................*/
function PR_H_arrow_left(){

}
function PR_H_arrow_right(){

}
/* flechas Mujeres...................*/
function PR_M_arrow_left(){

}
function PR_M_arrow_right(){

}