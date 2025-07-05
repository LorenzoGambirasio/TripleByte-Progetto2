    document.addEventListener("DOMContentLoaded", function () {
        // Inizializzazione di Select2 per il menu a tendina degli ospedali
        $('#id_codOspedale').select2({
            placeholder: "Seleziona un ospedale di destinazione",
            allowClear: true,
            width: "100%",
            theme: "bootstrap-5"
        });
    });