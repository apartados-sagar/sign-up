//const CONFIG = {
  //  API_URL: 'http://localhost:10000',
  //  API_KEY: 'fbx_WBePsq9IOwEkci72fwhIpvyvqnsDM1'  // MISMA que en Render
//};
const CONFIG = {
    API_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:10000'  // Local
        : 'https://back-end-0auy.onrender.com',  // Producción
    API_KEY: 'fbx_WBePsq9IOwEkci72fwhIpvyvqnsDM1'
};