document.addEventListener("DOMContentLoaded", function () {
            // Inizializzazione tooltip Bootstrap
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

            // JavaScript per i pulsanti di pulizia dei filtri (la "x")
            // Questi bottoni sono per input text e non per Select2
            document.querySelectorAll('.clear-filter-btn').forEach(button => {
                button.addEventListener('click', function () {
                    const targetId = this.dataset.target;
                    const targetField = document.getElementById(targetId);
                    if (targetField) {
                        if ($(targetField).hasClass('select2-hidden-accessible')) {
                            // Se è un Select2, usa il metodo Select2 per svuotarlo
                            $(targetField).val(null).trigger('change');
                        } else if (targetField.tagName === 'SELECT') {
                            // Per select normali non gestiti da Select2 (se ce ne sono)
                            targetField.value = '';
                        } else {
                            targetField.value = ''; // Svuota input text
                        }
                    }
                });
            });

            // Inizializzazione Select2 per il campo paziente in Ricoveri (nuovo record)
            $('#id_cittadino').select2({
                placeholder: "Seleziona un paziente",
                allowClear: true,
                width: '100%',
                language: {
                    noResults: function () { return "Nessun paziente trovato"; }
                }
            });

            // Inizializzazione Select2 per TUTTI i campi select con classe .select2-filter
            // Verrà eseguito dopo che filtro_template è stato incluso nel DOM
            $('.select2-filter').each(function () {
                var $this = $(this);
                // Inizializza solo se non già inizializzato da un precedente script (es. modals.html)
                if (!$this.data('select2')) {
                    $this.select2({
                        theme: "bootstrap-5",
                        placeholder: $this.data('placeholder') || "Seleziona", // Prende da data-placeholder o default
                        allowClear: true,
                        multiple: $this.attr('multiple') ? true : false, // Determina se è multiplo
                        closeOnSelect: $this.attr('multiple') ? false : true, // Chiudi solo se non multiplo
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
            // Le inizializzazioni Select2 all'interno dei modali (.on('shown.bs.modal')) rimangono in modals.html
            // per elementi che potrebbero non essere presenti al DOMContentLoaded (ma è buona pratica inizializzare tutto subito se è possibile)
        });