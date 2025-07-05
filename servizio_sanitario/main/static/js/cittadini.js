 document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.clickable-row').forEach(row => {
      row.addEventListener('click', function (event) {
        if (!event.target.closest('a') && !event.target.closest('button')) {
          window.location.href = row.dataset.href;
        }
      });
    });
  });