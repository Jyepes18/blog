document.getElementById("create").addEventListener("submit", function(event) {
    const title = document.getElementById("title").value;
    const exampleFormControlTextarea1 = document.getElementById("exampleFormControlTextarea1").value;

    if (title === "" || exampleFormControlTextarea1 === "") {
        Swal.fire({
            icon: 'error',
            title: 'Campos vacíos',
            text: 'Todos los campos son necesarios.',
        });
        event.preventDefault();  
    } 
});
