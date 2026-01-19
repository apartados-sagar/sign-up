import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyCZ0XEcKUKtbB7WiUAmaIbBf-UkqTgZYxY",
    authDomain: "apartados-sagar-1a901.firebaseapp.com",
    projectId: "apartados-sagar-1a901",
    storageBucket: "apartados-sagar-1a901.firebasestorage.app",
    messagingSenderId: "145902728046",
    appId: "1:145902728046:web:4468fb60b5d72cd4efc77f",
    measurementId: "G-ESJ7EXWH7Z"
};
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

const ADMINS = ['admin@apartadossagar.com'];

// Variable global para saber si es admin
let esAdmin = false;

// Verificar usuario al cargar
onAuthStateChanged(auth,(user) => {
    console.log('Estado de auth:', user);
    if (user) {
        // Verificar si es admin  
        esAdmin = ADMINS.includes(user.email);
        
        if (esAdmin) {
            try {
                    
                console.log('admin:', auth);
                document.getElementById('panel-admin').style.display = 'block';
            } catch (error) {
                console.log('Error al abrir modal:', error)
            }
        }
        else{
            console.log('usuario:', auth);
            window.location.href = '/index.html';
        }
    }
});

