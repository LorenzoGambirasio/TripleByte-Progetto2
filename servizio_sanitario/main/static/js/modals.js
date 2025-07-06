// NUOVO: flag per la validazione dell'autocompletamento
let indirizzoSelezionato = false;
let cittaSelezionata = false;

$(document).ready(function () {
    // Definizione di tutti i modali
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

    // Inizializzazione Tooltip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    // Gestione eventi per il modale di aggiunta ricovero
    $('#modaleAggiungi').on('show.bs.modal', function () {
        const form = $('#formAggiungiRicovero');
        if (form.length > 0) form[0].reset();
        $('#id_cittadino, #id_patologie, #id_codOspedale', this).val(null).trigger('change');
        const dataIngressoInput = document.getElementById('id_data_ingresso');
        if (!dataIngressoInput.value) { dataIngressoInput.valueAsDate = new Date(); }
        dataIngressoInput.max = new Date().toISOString().split("T")[0];
    });

    $('#modaleAggiungi').on('shown.bs.modal', function () {
        const modal = $(this);
        $('#id_cittadino', modal).select2({ theme: "bootstrap-5", dropdownParent: modal, placeholder: "Seleziona un paziente", allowClear: true, width: '100%' });
        $('#id_codOspedale', modal).select2({ theme: "bootstrap-5", dropdownParent: modal, placeholder: "Seleziona un ospedale", allowClear: true, width: '100%' });
        $('#id_patologie', modal).select2({
            theme: "bootstrap-5",
            dropdownParent: modal,
            placeholder: "Seleziona una o più patologie",
            allowClear: true,
            multiple: true,
            closeOnSelect: false,
            width: '100%'
        });
    });

    // Gestione invio form aggiunta ricovero
    $("#formAggiungiRicovero").on("submit", function (e) {
        e.preventDefault();
        const form = this;
        $.ajax({
            type: "POST", url: $(form).attr("action"), data: $(form).serialize(),
            success: function (data) {
                if (data.success) {
                    modals.aggiungi.hide();
                    Swal.fire({ icon: 'success', title: 'Ricovero aggiunto!', timer: 2000, showConfirmButton: false })
                        .then(() => window.location.reload());
                } else {
                    Swal.fire({ icon: 'error', title: 'Errore', html: Object.values(data.errors || {}).flat().join('<br>') });
                }
            },
            error: function () {
                Swal.fire('Errore', 'Si è verificato un problema durante la richiesta.', 'error');
            }
        });
    });

    // --- LOGICA PER IL FORM PAZIENTE SEPARATO ---

    // Gestisce la visibilità del campo CSSN in base alla provenienza
    $('input[name="provenienza"]').on('change', function () {
        if (this.value === 'Estero') {
            $('#container_cssn_nuovo').slideUp();
        } else {
            $('#container_cssn_nuovo').slideDown();
        }
    });

    // Gestisce l'invio del form del nuovo paziente
    $('#formNuovoPaziente').on('submit', function (e) {
        e.preventDefault();
        
        // --- NUOVA LOGICA DI VALIDAZIONE AUTOCOMPLETAMENTO ---
        const indirizzoInput = document.getElementById('id_indirizzo');
        const cittaInput = document.getElementById('id_citta');
        let formValido = true;
        let messaggioErrore = '';

        if (cittaInput.value.trim() !== '' && !cittaSelezionata) {
            messaggioErrore += 'Per "Luogo di Nascita" è obbligatorio selezionare una voce dall\'elenco dei suggerimenti.<br>';
            formValido = false;
        }

        if (indirizzoInput.value.trim() !== '' && !indirizzoSelezionato) {
            messaggioErrore += 'Per "Indirizzo" è obbligatorio selezionare una voce dall\'elenco dei suggerimenti.';
            formValido = false;
        }

        if (!formValido) {
            Swal.fire({
                icon: 'error',
                title: 'Selezione Obbligatoria',
                html: messaggioErrore,
            });
            return; // Interrompe l'invio del form
        }
        // --- FINE NUOVA LOGICA ---

        const form = $(this);
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
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
                } else {
                    const errori = Object.values(response.errors).map(e => e.join('<br>')).join('<br>');
                    Swal.fire('Errore di Validazione', errori, 'error');
                }
            },
            error: function () {
                Swal.fire('Errore', 'Impossibile comunicare con il server.', 'error');
            }
        });
    });

    // --- LOGICA PER GLI ALTRI MODALI (Dettagli, Modifica, etc.) ---
    // ... (il resto del file rimane invariato)
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
        switch (statoRicovero) {
            case 0: // Attivo
                setButtonState($('#btnModifica'), true);
                setButtonState($('#btnTrasferisci'), true);
                setButtonState($('#btnElimina'), true);
                setButtonState($('#btnDeceduto'), true);
                break;
            case 1: // Trasferito
                setButtonState($('#btnModifica'), false);
                setButtonState($('#btnTrasferisci'), false);
                setButtonState($('#btnElimina'), true);
                setButtonState($('#btnDeceduto'), false);
                $('#dettagliMsg').text("Azioni limitate: il ricovero è stato trasferito.").show();
                break;
            case 2: // Dimesso
                setButtonState($('#btnModifica'), true);
                setButtonState($('#btnTrasferisci'), false);
                setButtonState($('#btnElimina'), true);
                setButtonState($('#btnDeceduto'), false);
                $('#dettagliMsg').text("Azioni limitate: il paziente è stato dimesso.").show();
                break;
            default:
                setButtonState($('#btnModifica'), false);
                setButtonState($('#btnTrasferisci'), false);
                setButtonState($('#btnElimina'), true);
                setButtonState($('#btnDeceduto'), false);
                $('#dettagliMsg').text("Azioni non disponibili per questo ricovero.").show();
                break;
        }
        modals.dettagli.show();
    });

    // GESTIONE PULSANTI AZIONI
    $('#btnModifica').on('click', function (e) {
        e.preventDefault();
        if ($(this).hasClass('disabled')) return;

        const dettagli = activeRow.data('dettagli-json');
        const dataIngressoParts = dettagli['Data Ingresso'].split('/');

        $('#modificaRicoveroPk').val(activeRow.data('pk'));
        $('#modificaOspedaleNome').val(activeRow.data('ospedale-nome'));
        $('#modificaDataIngresso').val(`${dataIngressoParts[2]}-${dataIngressoParts[1]}-${dataIngressoParts[0]}`);
        $('#modificaDurata').val(parseInt(dettagli['Durata (gg)']));
        $('#modificaMotivo').val(activeRow.data('motivo'));
        $('#modificaCosto').val(parseFloat(dettagli['Costo'].replace('€ ', '').replace(',', '.')));

        const patologieCods = activeRow.data('patologie-json').map(p => p.cod).filter(Boolean);

        $('#id_patologie_modifica').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#modificaRicoveroModal'),
            placeholder: "Seleziona patologie",
            allowClear: true,
            multiple: true,
            closeOnSelect: false
        }).val(patologieCods).trigger('change');

        $('#modificaDataIngresso').prop('readonly', true).css('box-shadow', '');
        $('#pazienteDisplayContainer, #unlockPazienteBtn').show();
        const $pazienteSelectContainer = $('#pazienteSelectContainer');
        $pazienteSelectContainer.hide();
        if ($pazienteSelectContainer.find('select[name="CSSN"]').data('select2')) {
            $pazienteSelectContainer.find('select[name="CSSN"]').select2('destroy');
        }
        $('#modificaPazienteNome').text(activeRow.data('paziente-nome'));

        $('.invalid-feedback').text('');
        modals.dettagli.hide();
        modals.modifica.show();
    });

    $('#btnTrasferisci').on('click', function (e) {
        e.preventDefault();
        if ($(this).hasClass('disabled')) return;

        $('#trasferisciRicoveroPk').val(activeRow.data('pk'));
        $('#trasferisciNomePaziente').val(activeRow.data('paziente-nome'));
        $('#trasferisciOspedaleAttuale').val(activeRow.data('ospedale-nome'));

        $('#selectOspedaleTrasferimento').val(null).trigger('change');
        $('#selectOspedaleTrasferimento').select2({
            theme: "bootstrap-5",
            dropdownParent: $('#trasferisciModal'),
            placeholder: "Seleziona un ospedale"
        });
        modals.dettagli.hide();
        modals.trasferisci.show();
    });

    $('#btnElimina, #btnEliminaFromRiepilogo').on('click', function (e) {
        e.preventDefault();
        if ($(this).hasClass('disabled')) return;

        $('#eliminaRicoveroPk').val(activeRow.data('pk'));
        $('#eliminaNomePaziente').text(activeRow.data('paziente-nome'));
        $('#eliminaOspedaleNome').text(activeRow.data('ospedale-nome'));

        modals.dettagli.hide();
        modals.riepilogoDecesso.hide();
        modals.elimina.show();
    });

    $('#btnDeceduto, #btnModificaCausaDecesso').on('click', function (e) {
        e.preventDefault();
        $('#id_password').val('');
        $('#passwordError').text('');
        const isDeclare = $(this).is('#btnDeceduto');
        $('#passwordAction').val(isDeclare ? 'dichiara' : 'modificaCausa');
        modals.dettagli.hide();
        modals.riepilogoDecesso.hide();
        modals.password.show();
    });

    // LOGICA PER SBLOCCO CAMPI CON PASSWORD
    $('#modificaDataIngresso[readonly], #unlockPazienteBtn').on('click', function () {
        const isDate = $(this).is('#modificaDataIngresso');
        if (isDate && !$(this).is('[readonly]')) return;

        $('#id_password').val('');
        $('#passwordError').text('');
        $('#passwordAction').val('unlock_field');
        $('#decessoPasswordModal').data('target-field', isDate ? '#modificaDataIngresso' : '#pazienteDisplayContainer');
        modals.password.show();
    });

    // GESTIONE INVIO FORM GENERICO
    $('form:not(#formAggiungiRicovero, #filtriRicoveriForm, #formNuovoPaziente)').on('submit', function (e) {
        e.preventDefault();
        const form = $(this);
        const formId = form.attr('id');
        let url, pk, modalToHide, successTitle;

        if (formId === 'formVerificaPassword') {
            ajaxVerifyPassword();
            return;
        }

        switch (formId) {
            case 'formTrasferisci':
                pk = $('#trasferisciRicoveroPk').val();
                url = `/trasferisci_ricovero/${pk}/`;
                modalToHide = modals.trasferisci;
                successTitle = 'Trasferimento completato!';
                break;
            case 'formEliminaRicovero':
                pk = $('#eliminaRicoveroPk').val();
                url = `/elimina_ricovero/${pk}/`;
                modalToHide = modals.elimina;
                successTitle = 'Ricovero eliminato!';
                break;
            case 'formModificaRicovero':
                pk = $('#modificaRicoveroPk').val();
                url = `/modifica_ricovero/${pk}/`;
                modalToHide = modals.modifica;
                successTitle = 'Ricovero modificato!';
                break;
            case 'formDichiaraDecesso':
                pk = $('#dichiaraDecessoRicoveroPk').val();
                url = `/dichiara_decesso/${pk}/`;
                modalToHide = modals.dichiaraDecesso;
                successTitle = 'Decesso dichiarato!';
                break;
            case 'formModificaCausaDecesso':
                pk = $('#modificaCausaRicoveroPk').val();
                url = `/modifica_causa_decesso/${pk}/`;
                modalToHide = modals.modificaCausa;
                successTitle = 'Causa decesso modificata!';
                break;
            default: return;
        }

        $.ajax({
            type: "POST", url: url, data: form.serialize(),
            success: function (data) {
                if (data.success) {
                    modalToHide.hide();
                    Swal.fire({ icon: 'success', title: successTitle, timer: 2000, showConfirmButton: false }).then(() => window.location.reload());
                } else {
                    Swal.fire({ icon: 'error', title: 'Errore di validazione', html: Object.values(data.errors || {}).flat().join('<br>') });
                }
            },
            error: (xhr) => {
                let errorMsg = "Problema di comunicazione con il server.";
                if (xhr.responseJSON && xhr.responseJSON.errors) {
                    errorMsg = Object.values(xhr.responseJSON.errors).map(e => e.join('<br>')).join('<br>');
                }
                Swal.fire("Errore", errorMsg, "error");
            }
        });
    });

    function ajaxVerifyPassword() {
        const password = $('#id_password').val();
        const action = $('#passwordAction').val();
        $('#passwordError').text('');

        $.ajax({
            type: "POST", url: "/verifica_password/",
            data: { csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(), password: password },
            success: function (data) {
                if (data.success) {
                    modals.password.hide();
                    $('#id_password').val('');

                    if (action === 'unlock_field') {
                        const targetSelector = $('#decessoPasswordModal').data('target-field');
                        if (targetSelector === '#modificaDataIngresso') {
                            $(targetSelector).prop('readonly', false).focus().css('box-shadow', '0 0 0 .25rem rgba(13, 110, 253, .25)');
                            setTimeout(() => $(targetSelector).css('box-shadow', ''), 2000);
                        } else if (targetSelector === '#pazienteDisplayContainer') {
                            const selectPazienteContainer = $('#pazienteSelectContainer');
                            const selectPaziente = selectPazienteContainer.find('select[name="CSSN"]');
                            const currentPazienteCSSN = activeRow.data('dettagli-json')['CSSN'];

                            $('#pazienteDisplayContainer, #unlockPazienteBtn').hide();
                            selectPazienteContainer.show();

                            selectPaziente.select2({
                                theme: "bootstrap-5",
                                dropdownParent: $('#modificaRicoveroModal')
                            }).val(currentPazienteCSSN).trigger('change');
                        }
                    } else if (action === 'dichiara') {
                        $('#dichiaraDecessoNomePaziente').text(activeRow.data('paziente-nome'));
                        $('#dichiaraDecessoRicoveroPk').val(activeRow.data('pk'));
                        const now = new Date();
                        const localDateTimeString = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}T${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
                        $('#id_data_ora_decesso_dichiara').val(localDateTimeString);
                        $('#id_causa_decesso_dichiara').val('');
                        modals.dichiaraDecesso.show();
                    } else if (action === 'modificaCausa') {
                        $('#modificaCausaRicoveroPk').val(activeRow.data('pk'));
                        $('#id_data_ora_decesso_modifica').val(activeRow.data('decesso-data'));
                        $('#id_causa_decesso_modifica').val(activeRow.data('decesso-causa'));
                        modals.modificaCausa.show();
                    }
                } else {
                    $('#passwordError').text((data.errors && data.errors[0]) || 'Password non corretta.').show();
                }
            },
            error: () => $('#passwordError').text('Problema di comunicazione.').show()
        });
    }
});

function initAutocompleteManuale() {
  const inputIndirizzo = document.getElementById('id_indirizzo');
  const suggerimentiIndirizzo = document.getElementById('suggerimenti_indirizzo');

  const inputCitta = document.getElementById('id_citta');
  const suggerimentiCitta = document.getElementById('suggerimenti_citta');

  if (inputIndirizzo) {
    inputIndirizzo.addEventListener('input', function () {
      indirizzoSelezionato = false; // NUOVO: Resetta il flag quando l'utente scrive
      cercaSuggerimenti(this.value, 'address', suggerimentiIndirizzo, inputIndirizzo);
    });
  }

  if (inputCitta) {
    inputCitta.addEventListener('input', function () {
      cittaSelezionata = false; // NUOVO: Resetta il flag quando l'utente scrive
      cercaSuggerimenti(this.value, '(cities)', suggerimentiCitta, inputCitta);
    });
  }

  // Chiudi i suggerimenti se clicchi fuori
  document.addEventListener('click', function (e) {
    if (!e.target.closest('#id_indirizzo') && !e.target.closest('#suggerimenti_indirizzo')) {
      suggerimentiIndirizzo.innerHTML = '';
    }
    if (!e.target.closest('#id_citta') && !e.target.closest('#suggerimenti_citta')) {
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
    types: [tipo],
    componentRestrictions: { country: 'it' }
  }, function (predictions, status) {
    contenitore.innerHTML = '';

    if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
      return;
    }

    predictions.slice(0, 5).forEach(p => {
      const li = document.createElement('li');
      li.className = 'list-group-item list-group-item-action';
      li.textContent = p.description;
      li.addEventListener('click', function () {
        input.value = p.description;
        contenitore.innerHTML = '';
        // NUOVO: Imposta il flag corretto a true dopo la selezione
        if (input.id === 'id_indirizzo') {
            indirizzoSelezionato = true;
        } else if (input.id === 'id_citta') {
            cittaSelezionata = true;
        }
      });
      contenitore.appendChild(li);
    });
  });
}

$('#modaleNuovoPaziente').on('shown.bs.modal', function () {
  // NUOVO: Resetta i flag ogni volta che il modale viene mostrato
  indirizzoSelezionato = false;
  cittaSelezionata = false;
  initAutocompleteManuale();
});