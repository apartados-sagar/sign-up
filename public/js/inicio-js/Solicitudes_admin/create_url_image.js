export function create_url(select_area, select_genero, nombre){
    // switch para desbloquar el area camisas o pantalones ect.
    let area;
    let genero;

    switch (select_area) {
        case "c_":
            area = "camisas/";
            break;
        case "p_":
            area = "pantalones/";
            break;
        case "j_":
            area = "joyeria/";
            break;
        case "pr_":
            area = "perfumeria/";
            break;
        default:
            area = "area invalidad"; 
            return "error area";
    }

    switch (select_genero) {
        case "h":
            genero = "hombres/";
            break;
        case "m":
            genero = "mujeres/";
            break;
            
        default:
            genero = "genero invalido";
            return "error area";
    }
    const url =  area + genero  + nombre;
    return url;
}