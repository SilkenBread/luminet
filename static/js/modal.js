/**
 * Sistema de Modales Genéricos - Luminet
 * Modales nativos HTML con Tailwind CSS
 * 
 * Uso:
 *   openModal('modalId')   - Abre un modal por su ID
 *   closeModal('modalId')  - Cierra un modal por su ID
 * 
 * HTML:
 *   <div id="miModal" class="modal-overlay ..."> ... </div>
 *   <button data-modal-open="miModal">Abrir</button>
 *   <button data-modal-close="miModal">Cerrar</button>
 */

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');

    // Trigger animation
    requestAnimationFrame(() => {
        modal.classList.add('modal-active');
    });

    // Re-init lucide icons inside the modal
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.remove('modal-active');

    // Wait for transition to finish before hiding
    setTimeout(() => {
        modal.classList.add('hidden');
        // Only remove overflow-hidden if no other modals are open
        const openModals = document.querySelectorAll('.modal-overlay:not(.hidden)');
        if (openModals.length === 0) {
            document.body.classList.remove('overflow-hidden');
        }
    }, 200);
}

// Event delegation for data attributes
document.addEventListener('click', function (e) {
    // Open modal
    const openTrigger = e.target.closest('[data-modal-open]');
    if (openTrigger) {
        e.preventDefault();
        openModal(openTrigger.getAttribute('data-modal-open'));
        return;
    }

    // Close modal  
    const closeTrigger = e.target.closest('[data-modal-close]');
    if (closeTrigger) {
        e.preventDefault();
        closeModal(closeTrigger.getAttribute('data-modal-close'));
        return;
    }

    // Close on backdrop click
    if (e.target.classList.contains('modal-overlay') && e.target.classList.contains('modal-active')) {
        const modalId = e.target.id;
        if (modalId) {
            closeModal(modalId);
        }
    }
});

// Close on ESC key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal-overlay.modal-active');
        // Close the last opened modal (topmost)
        if (openModals.length > 0) {
            const lastModal = openModals[openModals.length - 1];
            closeModal(lastModal.id);
        }
    }
});
