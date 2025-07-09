let ultimoLuogoNascitaSelezionato = null;
let ultimoIndirizzoSelezionato = null;

function pulisciErroriForm(formElement) {
    if (formElement && formElement.length) {
        formElement.find('.is-invalid').removeClass('is-invalid');
        formElement.find('.select2-container.is-invalid').removeClass('is-invalid');
        formElement.find('.invalid-feedback').remove();
    }
}

function gestisciErroriForm(formElement, errors) {
    pulisciErroriForm(formElement);
    if (errors['__all__']) {
        Swal.fire({
            icon: 'error',
            title: 'Errore di Validazione',
            html: errors['__all__'].join('<br>')
        });
    }
    for (const fieldName in errors) {
        if (fieldName === '__all__') continue;
        const errorMessages = errors[fieldName];
        let field = formElement.find(`[name="${fieldName}"], [name^="${fieldName}["]`);
        if (field.length) {
            let fieldToInvalidate = field.hasClass('select2-hidden-accessible') ? field.next('.select2-container') : field;
            fieldToInvalidate.addClass('is-invalid');
            const errorHtml = `<div class="invalid-feedback d-block">${errorMessages.join('<br>')}</div>`;
            let container = fieldToInvalidate.parent();
            if (field.hasClass('select2-hidden-accessible') || container.hasClass('input-group')) {
                fieldToInvalidate.parent().append(errorHtml);
            } else {
                fieldToInvalidate.after(errorHtml);
            }
        }
    }
}

function handleAjaxError(form, xhr) {
    if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.errors) {
        const errors = xhr.responseJSON.errors;
        gestisciErroriForm(form, errors);
        if (!errors['__all__'] && Object.keys(errors).length > 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Attenzione',
                text: 'Alcuni campi non sono validi. Controlla i messaggi di errore.',
            });
        }
    } else if (xhr.status === 500) {
        Swal.fire('Errore Server', 'Si è verificato un problema interno al server. Riprova più tardi.', 'error');
    } else {
        Swal.fire('Errore di Rete', 'Impossibile comunicare con il server. Controlla la tua connessione.', 'error');
    }
}

$(document).ready(function () {
    const modals = {
        aggiungi: new bootstrap.Modal(document.getElementById('modaleAggiungi')),
        nuovoPaziente: new bootstrap.Modal(document.getElementById('modaleNuovoPaziente')),
        dettagli: new bootstrap.Modal(document.getElementById('dettagliModal')),
        trasferisci: new bootstrap.Modal(document.getElementById('trasferisciModal')),
        elimina: new bootstrap.Modal(document.getElementById('eliminaRicoveroModal')),
        modifica: new bootstrap.Modal(document.getElementById('modificaRicoveroModal')),
        password: new bootstrap.Modal(document.getElementById('decessoPasswordModal')),
        dichiaraDecesso: new bootstrap.Modal(document.getElementById('dichiaraDecessoModal')),
        riepilogoDecesso: new bootstrap.Modal(document.getElementById('riepilogoDecessoModal')),
        modificaCausa: new bootstrap.Modal(document.getElementById('modificaCausaDecessoModal'))
    };

    let activeRow;

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    $('.modal').on('show.bs.modal', function() {
        pulisciErroriForm($(this).find('form'));
    });

    $('#modaleAggiungi').on('show.bs.modal', function () {
        const form = $(this).find('form');
        if (form.length > 0) {
            form[0].reset();
        }
        $('#id_cittadino, #id_codOspedale, #id_patologie', this).val(null).trigger('change');
        const dataIngressoInput = document.getElementById('id_data_ingresso');
        if (dataIngressoInput) {
            dataIngressoInput.valueAsDate = new Date();
        }
    });

    $('#formNuovoPaziente').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        if ((document.getElementById('id_citta').value.trim() !== '' && document.getElementById('id_citta').value.trim() !== ultimoLuogoNascitaSelezionato) ||
            (document.getElementById('id_indirizzo').value.trim() !== '' && document.getElementById('id_indirizzo').value.trim() !== ultimoIndirizzoSelezionato)) {
            Swal.fire('Selezione Obbligatoria', 'Per "Luogo di Nascita" e "Indirizzo" è necessario selezionare una voce valida dall\'elenco.', 'error');
            return;
        }
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    const paziente = response.paziente;
                    const nuovaOpzione = new Option(`${paziente.cssn} - ${paziente.nome_completo}`, paziente.cssn, true, true);
                    $('#id_cittadino').append(nuovaOpzione).trigger('change');
                    modals.nuovoPaziente.hide();
                    let successMessage = `Nuovo paziente <strong>${paziente.nome_completo}</strong> aggiunto e selezionato.`;
                    if (paziente.cssn.startsWith('EST')) {
                        successMessage += `<br><br>Codice Estero generato: <strong>${paziente.cssn}</strong>`;
                    }
                    Swal.fire({ icon: 'success', title: 'Successo!', html: successMessage });
                }
            },
            error: function(xhr) {
                handleAjaxError(form, xhr);
            }
        });
    });
    
    function handleGenericFormSubmit(e) {
        e.preventDefault();
        const form = $(this);
        const formId = form.attr('id');
        const procediConSalvataggio = () => {
            let url = form.attr('action');
            let successTitle = 'Operazione completata con successo!';
            switch(formId) {
                case 'formAggiungiRicovero': successTitle = 'Ricovero aggiunto con successo!'; break;
                case 'formTrasferisci': url = `/trasferisci_ricovero/${$('#trasferisciRicoveroPk').val()}/`; successTitle = 'Trasferimento completato!'; break;
                case 'formEliminaRicovero': url = `/elimina_ricovero/${$('#eliminaRicoveroPk').val()}/`; successTitle = 'Ricovero eliminato!'; break;
                case 'formModificaRicovero': url = `/modifica_ricovero/${$('#modificaRicoveroPk').val()}/`; successTitle = 'Ricovero modificato!'; break;
                case 'formDichiaraDecesso': url = `/dichiara_decesso/${$('#dichiaraDecessoRicoveroPk').val()}/`; successTitle = 'Decesso dichiarato!'; break;
                case 'formModificaCausaDecesso': url = `/modifica_causa_decesso/${$('#modificaCausaRicoveroPk').val()}/`; successTitle = 'Dati del decesso aggiornati!'; break;
                case 'formVerificaPassword': url = '/verifica_password/'; break;
            }
            $.ajax({
                type: 'POST',
                url: url,
                data: form.serialize(),
                success: function(response) {
                    if (response.success) {
                        if (formId === 'formVerificaPassword') {
                            modals.password.hide();
                            const action = $('#passwordAction').val();
                            if (action === 'dichiara') {
                                const dettagliRicovero = activeRow.data('dettagli-json');
                                const dataIngresso = dettagliRicovero['Data Ingresso'];
                                $('#infoDataRicovero').html(
                                    `<i class="bi bi-info-circle-fill me-1"></i> Data ricovero: <strong>${dataIngresso}</strong>. La data del decesso non può essere precedente.`
                                );
                                $('#dichiaraDecessoNomePaziente').text(activeRow.data('paziente-nome'));
                                $('#dichiaraDecessoRicoveroPk').val(activeRow.data('pk'));
                                const now = new Date();
                                const year = now.getFullYear();
                                const month = (now.getMonth() + 1).toString().padStart(2, '0');
                                const day = now.getDate().toString().padStart(2, '0');
                                const hours = now.getHours().toString().padStart(2, '0');
                                const minutes = now.getMinutes().toString().padStart(2, '0');
                                const localDateTimeString = `${year}-${month}-${day}T${hours}:${minutes}`;
                                $('#id_data_ora_decesso_dichiara').val(localDateTimeString);
                                $('#id_causa_decesso_dichiara').val('');
                                modals.dichiaraDecesso.show();
                            } else if (action === 'modificaCausa') {
                                $('#modificaCausaRicoveroPk').val(activeRow.data('pk'));
                                $('#id_data_ora_decesso_modifica').val(activeRow.data('decesso-data'));
                                $('#id_causa_decesso_modifica').val(activeRow.data('decesso-causa'));
                                modals.modificaCausa.show();
                            } else if (action === 'unlock_field') {
                                const targetSelector = $('#decessoPasswordModal').data('target-field');
                                if (targetSelector === '#modificaDataIngresso') {
                                    $(targetSelector).prop('readonly', false).focus();
                                } else if (targetSelector === '#pazienteDisplayContainer') {
                                    $('#pazienteDisplayContainer, #unlockPazienteBtn').hide();
                                    $('#pazienteSelectContainer').show().find('select').select2({
                                        theme: "bootstrap-5",
                                        dropdownParent: $('#modificaRicoveroModal')
                                    });
                                }
                            }
                        } else {
                           $('.modal').modal('hide');
                           Swal.fire({ icon: 'success', title: successTitle, timer: 2000, showConfirmButton: false })
                               .then(() => window.location.reload());
                        }
                    }
                },
                error: function(xhr) {
                    handleAjaxError(form, xhr);
                }
            });
        };
        if (formId === 'formAggiungiRicovero') {
            const dataIngressoInput = document.getElementById('id_data_ingresso');
            const selectedDate = new Date(dataIngressoInput.value);
            const today = new Date();
            selectedDate.setHours(0, 0, 0, 0);
            today.setHours(0, 0, 0, 0);
            if (selectedDate < today) {
                Swal.fire({
                    title: 'Data nel passato',
                    text: "Attenzione: hai selezionato una data di ingresso antecedente a oggi. Vuoi procedere comunque?",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#6e757c',
                    confirmButtonText: 'Sì, procedi',
                    cancelButtonText: 'Annulla'
                }).then((result) => {
                    if (result.isConfirmed) {
                        procediConSalvataggio();
                    }
                });
            } else {
                procediConSalvataggio();
            }
        } else {
            procediConSalvataggio();
        }
    }

    const formIDs = '#formAggiungiRicovero, #formTrasferisci, #formEliminaRicovero, #formModificaRicovero, #formDichiaraDecesso, #formModificaCausaDecesso, #formVerificaPassword';
    $(document).on('submit', formIDs, handleGenericFormSubmit);
    
    $('#modaleAggiungi').on('shown.bs.modal', function () {
        const modal = $(this);
        $('#id_cittadino', modal).select2({ theme: "bootstrap-5", dropdownParent: modal, placeholder: "Seleziona un paziente", allowClear: true, width: '100%' });
        $('#id_codOspedale', modal).select2({ theme: "bootstrap-5", dropdownParent: modal, placeholder: "Seleziona un ospedale", allowClear: true, width: '100%' });
        $('#id_patologie', modal).select2({ theme: "bootstrap-5", dropdownParent: modal, placeholder: "Seleziona patologie", allowClear: true, multiple: true, closeOnSelect: false, width: '100%' });
    });

    $('input[name="provenienza"]').on('change', function () {
        if (this.value === 'Estero') $('#container_cssn_nuovo').slideUp(); else $('#container_cssn_nuovo').slideDown();
    });

    $(document).on('click', '.clickable-row', function () {
        activeRow = $(this);
        const dettagli = activeRow.data('dettagli-json');
        if (activeRow.data('paziente-deceduto') === 1) {
            $('#riepilogoDecessoNomePaziente').text(activeRow.data('paziente-nome'));
            $('#riepilogoDecessoDataOra').text(activeRow.data('decesso-data').replace('T', ' ') || 'Non specificata');
            $('#riepilogoDecessoCausa').text(activeRow.data('decesso-causa') || 'Non specificata');
            modals.riepilogoDecesso.show();
            return;
        }
        $('#dettagliContenuto').empty().append(Object.keys(dettagli).map(key => `<div class="mb-2"><strong class="text-secondary">${key}:</strong> <span class="fw-bold">${dettagli[key]}</span></div>`));
        const patologie = activeRow.data('patologie-json');
        const patologieContainer = $('#dettagliPatologie').empty();
        if (patologie && patologie.length > 0) {
            patologie.forEach(p => patologieContainer.append(`<span class="badge bg-bordeaux rounded-pill me-1 mb-1">${p.nome}</span>`));
        } else {
            patologieContainer.append('<span class="text-muted small">Nessuna patologia associata.</span>');
        }
        const statoRicovero = activeRow.data('stato');
        const setButtonState = (button, enabled) => button.toggleClass('disabled', !enabled).css('pointer-events', enabled ? 'auto' : 'none');
        $('#dettagliMsg').hide();
        setButtonState($('#btnModifica'), statoRicovero === 0 || statoRicovero === 2);
        setButtonState($('#btnTrasferisci'), statoRicovero === 0);
        setButtonState($('#btnElimina'), true);
        setButtonState($('#btnDeceduto'), statoRicovero === 0);
        if (statoRicovero === 1) $('#dettagliMsg').text("Azioni limitate: il ricovero è stato trasferito.").show();
        if (statoRicovero === 2) $('#dettagliMsg').text("Azioni limitate: il paziente è stato dimesso.").show();
        modals.dettagli.show();
    });

    $('#btnModifica').on('click', function (e) {
        e.preventDefault();
        if ($(this).hasClass('disabled')) return;
        
        $('#modificaDataIngresso').prop('readonly', true);
        $('#pazienteDisplayContainer, #unlockPazienteBtn').show();
        $('#pazienteSelectContainer').hide();

        const dettagli = activeRow.data('dettagli-json');
        const dataIngressoParts = dettagli['Data Ingresso'].split('/');
        $('#modificaRicoveroPk').val(activeRow.data('pk'));
        $('#modificaPazienteNome').text(dettagli['Paziente']);
        $('#modificaOspedaleNome').val(activeRow.data('ospedale-nome'));
        $('#modificaDataIngresso').val(`${dataIngressoParts[2]}-${dataIngressoParts[1]}-${dataIngressoParts[0]}`);
        $('#modificaDurata').val(parseInt(dettagli['Durata (gg)']));
        $('#modificaMotivo').val(activeRow.data('motivo'));
        $('#modificaCosto').val(parseFloat(dettagli['Costo'].replace('€ ', '').replace(',', '.')));
        const patologieCods = activeRow.data('patologie-json').map(p => p.cod).filter(Boolean);
        $('#id_patologie_modifica').select2({
            theme: "bootstrap-5", dropdownParent: $('#modificaRicoveroModal'), placeholder: "Seleziona patologie",
            allowClear: true, multiple: true, closeOnSelect: false
        }).val(patologieCods).trigger('change');
        modals.dettagli.hide();
        modals.modifica.show();
    });

    $('#btnTrasferisci').on('click', function (e) {
        e.preventDefault(); if ($(this).hasClass('disabled')) return;
        $('#trasferisciRicoveroPk').val(activeRow.data('pk'));
        $('#trasferisciNomePaziente').val(activeRow.data('paziente-nome'));
        $('#trasferisciOspedaleAttuale').val(activeRow.data('ospedale-nome'));
        $('#selectOspedaleTrasferimento').val(null).trigger('change').select2({
            theme: "bootstrap-5", dropdownParent: $('#trasferisciModal'), placeholder: "Seleziona un ospedale"
        });
        modals.dettagli.hide(); modals.trasferisci.show();
    });

    $('#btnElimina, #btnEliminaFromRiepilogo').on('click', function (e) {
        e.preventDefault(); if ($(this).hasClass('disabled')) return;
        $('#eliminaRicoveroPk').val(activeRow.data('pk'));
        $('#eliminaNomePaziente').text(activeRow.data('paziente-nome'));
        $('#eliminaOspedaleNome').text(activeRow.data('ospedale-nome'));
        modals.dettagli.hide(); modals.riepilogoDecesso.hide(); modals.elimina.show();
    });

    $('#btnDeceduto, #btnModificaCausaDecesso').on('click', function (e) {
        e.preventDefault();
        $('#passwordAction').val($(this).is('#btnDeceduto') ? 'dichiara' : 'modificaCausa');
        modals.dettagli.hide(); modals.riepilogoDecesso.hide(); modals.password.show();
    });
    
    $('#modificaDataIngresso[readonly], #unlockPazienteBtn').on('click', function () {
        const isDate = $(this).is('#modificaDataIngresso');
        if (isDate && !$(this).is('[readonly]')) return;
        $('#passwordAction').val('unlock_field');
        $('#decessoPasswordModal').data('target-field', isDate ? '#modificaDataIngresso' : '#pazienteDisplayContainer');
        modals.password.show();
    });
});

function initAutocompleteManuale() {
    const inputIndirizzo = document.getElementById('id_indirizzo');
    const suggerimentiIndirizzo = document.getElementById('suggerimenti_indirizzo');
    const inputCitta = document.getElementById('id_citta');
    const suggerimentiCitta = document.getElementById('suggerimenti_citta');

    if (inputIndirizzo) {
        inputIndirizzo.addEventListener('input', function () {
            ultimoIndirizzoSelezionato = null;
            cercaSuggerimenti(this.value, 'address', suggerimentiIndirizzo, inputIndirizzo);
        });
    }
    if (inputCitta) {
        inputCitta.addEventListener('input', function () {
            ultimoLuogoNascitaSelezionato = null;
            cercaSuggerimenti(this.value, '(cities)', suggerimentiCitta, inputCitta);
        });
    }
    document.addEventListener('click', function (e) {
        if (suggerimentiIndirizzo && !e.target.closest('#id_indirizzo') && !e.target.closest('#suggerimenti_indirizzo')) {
            suggerimentiIndirizzo.innerHTML = '';
        }
        if (suggerimentiCitta && !e.target.closest('#id_citta') && !e.target.closest('#suggerimenti_citta')) {
            suggerimentiCitta.innerHTML = '';
        }
    });
}

function cercaSuggerimenti(query, tipo, contenitore, input) {
    if (query.length < 3) {
        contenitore.innerHTML = '';
        return;
    }
    const service = new google.maps.places.AutocompleteService();
    service.getPlacePredictions({
        input: query,
        types: [tipo]
    }, function (predictions, status) {
        contenitore.innerHTML = '';
        if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) return;
        predictions.slice(0, 5).forEach(p => {
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-action';
            li.textContent = p.description;
            li.addEventListener('click', function () {
                input.value = p.description;
                contenitore.innerHTML = '';
                if (input.id === 'id_indirizzo') {
                    ultimoIndirizzoSelezionato = p.description;
                } else if (input.id === 'id_citta') {
                    ultimoLuogoNascitaSelezionato = p.description;
                }
            });
            contenitore.appendChild(li);
        });
    });
}

$('#modaleNuovoPaziente').on('shown.bs.modal', function () {
    ultimoLuogoNascitaSelezionato = null;
    ultimoIndirizzoSelezionato = null;
    const form = $(this).find('form');
    if(form.length) form[0].reset();
    initAutocompleteManuale();
});