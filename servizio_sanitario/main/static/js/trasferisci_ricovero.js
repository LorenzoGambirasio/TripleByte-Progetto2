    document.addEventListener("DOMContentLoaded", function () {
        $('#id_codOspedale').select2({
            placeholder: "Seleziona un ospedale di destinazione",
            allowClear: true,
            width: "100%",
            theme: "bootstrap-5"
        });
    });