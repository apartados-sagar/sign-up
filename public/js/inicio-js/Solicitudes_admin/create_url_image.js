export function create_url(select_genero, nombre){
    // Nota: 'select_area' se usa para buscar el bucket, pero no se incluye en la URL del objeto.
    let genero;

    switch (select_genero) {
        case "h":
            genero = "/hombres/";
            break;
        case "m":
            genero = "/mujeres/";
            break;
            
        default:
            genero = "genero invalido";
            return "error genero"; // Cambié a 'error genero' ya que 'area' no se usa aquí directamente
    }
    const url =  genero  + nombre; // Solo genero y nombre del archivo
    return url;
}