    document.addEventListener('DOMContentLoaded', function() {
        const righePerPageSelect = document.getElementById('righe-per-pagina');
        if (righePerPageSelect) {
            righePerPageSelect.addEventListener('change', function() {
                const perPage = this.value;
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('per_page', perPage);
                currentUrl.searchParams.set('page', 1); 
                window.location.href = currentUrl.toString();
            });
        }

        const jumpToPageLinks = document.querySelectorAll('.jump-to-page .page-link');
        jumpToPageLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const parentLi = this.closest('.jump-to-page');
                const totalPages = parseInt(parentLi.dataset.totalPages);
                const currentPage = parseInt(parentLi.dataset.currentPage);

                Swal.fire({
                    title: 'Vai a pagina',
                    input: 'text',
                    inputLabel: `Inserisci un numero di pagina (da 1 a ${totalPages})`,
                    inputPlaceholder: 'Numero pagina',
                    inputValue: currentPage,
                    showCancelButton: true,
                    confirmButtonText: 'Vai',
                    cancelButtonText: 'Annulla',
                    showLoaderOnConfirm: true,
                    preConfirm: (value) => {
                        const pageNum = parseInt(value);
                        
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
