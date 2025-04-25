// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add fade-in animation class to main content
    const mainContent = document.querySelector('.container.mt-4');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }

    // Handle book search form submission
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[type="search"]');
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'btn btn-sm position-absolute end-0 top-50 translate-middle-y text-muted d-none';
        clearButton.innerHTML = '<i class="bi bi-x-circle"></i>';
        clearButton.style.right = '50px';
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.focus();
            this.classList.add('d-none');
        });
        
        searchForm.appendChild(clearButton);
        
        searchInput.addEventListener('input', function() {
            if (this.value.length > 0) {
                clearButton.classList.remove('d-none');
            } else {
                clearButton.classList.add('d-none');
            }
        });
        
        // Trigger input event to initialize clear button visibility
        searchInput.dispatchEvent(new Event('input'));
    }

    // Handle book filter form
    const filterForm = document.getElementById('bookFilterForm');
    if (filterForm) {
        const filterSelects = filterForm.querySelectorAll('select');
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }

    // Handling confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // Book cover fallback
    const bookCovers = document.querySelectorAll('.book-cover');
    bookCovers.forEach(cover => {
        cover.addEventListener('error', function() {
            this.src = '/static/img/default_cover.jpg';
        });
    });

    // Form validation styling
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Dynamic year in copyright
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
});