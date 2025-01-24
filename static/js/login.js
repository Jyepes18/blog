document.getElementById("login").addEventListener("submit", function(event) {
    const exampleInputEmail1 = document.getElementById("exampleInputEmail1").value;
    const password = document.getElementById("password").value;

    if (exampleInputEmail1 === "" || password === "") {
        Swal.fire({
            icon: 'error',
            title: 'Campos vacíos',
            text: 'Todos los campos son necesarios.',
        });
        event.preventDefault();  
    } 
});
