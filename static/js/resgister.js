document.getElementById("register").addEventListener("submit", function(event) {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const repeatPassword = document.getElementById("repeat-password").value;

    let expresion_regular_contra = /^(?=.*[A-Z])(?=.*\d)(?=.*[a-z]).+$/;

    // Validación de campos vacíos
    if (name === "" || email === "" || password === "" || repeatPassword === "") {
        Swal.fire({
            icon: 'error',
            title: 'Campos vacíos',
            text: 'Todos los campos son necesarios.',
        });
        event.preventDefault();  
    } 
    // Validación de la contraseña
    else if (!expresion_regular_contra.test(password)) {
        Swal.fire({
            icon: 'error',
            title: 'Contraseña inválida',
            text: 'La contraseña debe tener al menos una mayúscula, una minúscula y un número.',
        });
        event.preventDefault();  
    } 
    // Validación de las contraseñas coincidentes
    else if (password !== repeatPassword) {
        Swal.fire({
            icon: 'error',
            title: 'Contraseñas no coinciden',
            text: 'Las contraseñas no coinciden. Por favor, inténtelo de nuevo.',
        });
        event.preventDefault();  
    }
});
