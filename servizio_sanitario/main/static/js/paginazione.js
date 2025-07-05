    document.addEventListener('DOMContentLoaded', function() {
        // Gestione cambio righe per pagina
        const righePerPageSelect = document.getElementById('righe-per-pagina');
        if (righePerPageSelect) {
            righePerPageSelect.addEventListener('change', function() {
                const perPage = this.value;
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('per_page', perPage);
                currentUrl.searchParams.set('page', 1); // Reset alla prima pagina quando cambia per_page
                window.location.href = currentUrl.toString();
            });
        }

        // Gestione "Vai a pagina..." (puntini)
        const jumpToPageLinks = document.querySelectorAll('.jump-to-page .page-link');
        jumpToPageLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const parentLi = this.closest('.jump-to-page');
                const totalPages = parseInt(parentLi.dataset.totalPages);
                const currentPage = parseInt(parentLi.dataset.currentPage);

                Swal.fire({
                    title: 'Vai a pagina',
                    input: 'text', // CAMBIATO A type="text"
                    inputLabel: `Inserisci un numero di pagina (da 1 a ${totalPages})`,
                    inputPlaceholder: 'Numero pagina',
                    inputValue: currentPage,
                    showCancelButton: true,
                    confirmButtonText: 'Vai',
                    cancelButtonText: 'Annulla',
                    showLoaderOnConfirm: true,
                    preConfirm: (value) => {
                        const pageNum = parseInt(value);
                        // Validazione più robusta per assicurarsi che sia un numero intero valido
                        if (isNaN(pageNum) || !Number.isInteger(pageNum) || pageNum < 1 || pageNum > totalPages) {
                            Swal.showValidationMessage(`Inserisci un numero intero valido tra 1 e ${totalPages}.`);
                            return false;
                        }
                        return pageNum;
                    },
                    allowOutsideClick: () => !Swal.isLoading()
                }).then((result) => {
                    if (result.isConfirmed) {
                        const pageNumber = result.value;
                        const currentUrl = new URL(window.location.href);
                        currentUrl.searchParams.set('page', pageNumber);
                        window.location.href = currentUrl.toString();
                    }
                });
            });
        });
    });
