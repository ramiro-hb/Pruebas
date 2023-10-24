// dashboard.js

function actualizarDatos() {
    $.ajax({
        url: '/obtener_datos', // Ruta en Flask para obtener los datos
        type: 'GET',
        dataType: 'json', // Esperamos datos en formato JSON
        success: function (data) {
            // Actualiza los elementos HTML con los nuevos datos
            $('#valor-sensor').text('Valor del Sensor: ' + data.sensor_data);
            $('#voltaje').text('Voltaje: ' + data.voltage + ' V');
            $('#corriente').text('Corriente: ' + data.current + ' A');
        },
        complete: function () {
            // Llama a esta función nuevamente después de un intervalo de tiempo (por ejemplo, 1 segundo)
            setTimeout(actualizarDatos, 1000); // Actualiza cada 1 segundo
        }
    });
}

// Llama a la función para iniciar la actualización de datos
actualizarDatos();
