document.addEventListener("DOMContentLoaded", function () {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    document.querySelectorAll('.clear-filter-btn').forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.dataset.target;
            const targetField = document.getElementById(targetId);
            if (targetField) {
                if ($(targetField).hasClass('select2-hidden-accessible')) {
                    $(targetField).val(null).trigger('change');
                } else if (targetField.tagName === 'SELECT') {
                    targetField.value = '';
                } else {
                    targetField.value = '';
                }
            }
        });
    });

    $('#id_cittadino').select2({
        placeholder: "Seleziona un paziente",
        allowClear: true,
        width: '100%',
        language: {
            noResults: function () { return "Nessun paziente trovato"; }
        }
    });

    $('.select2-filter').each(function () {
        var $this = $(this);
        if (!$this.data('select2')) {
            $this.select2({
                theme: "bootstrap-5",
                placeholder: $this.data('placeholder') || "Seleziona",
                allowClear: true,
                multiple: $this.attr('multiple') ? true : false,
                closeOnSelect: $this.attr('multiple') ? false : true,
                language: {
                    noResults: function () { return "Nessun risultato"; },
                    removeAllItems: function () { return "Rimuovi tutti"; },
                    selected: function (args) {
                        if (args.data && args.data.length > 0) {
                            return args.data.length + ' selezionati';
                        }
                        return 'Seleziona';
                    }
                }
            });
        }
    });
});