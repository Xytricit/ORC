// Black-themed Modal System
class ModalManager {
    constructor() {
        this.currentModal = null;
    }

    show(options) {
        const {
            title = 'Alert',
            message = '',
            type = 'info',
            confirmText = 'OK',
            cancelText = null,
            onConfirm = null,
            onCancel = null,
            closeOnOverlay = true
        } = options;

        // Remove existing modal if any
        this.close();

        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const icon = icons[type] || icons.info;

        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-icon ${type}">${icon}</div>
                    <div class="modal-header-content">
                        <h3 class="modal-title">${title}</h3>
                    </div>
                    <button class="modal-close" aria-label="Close">&times;</button>
                </div>
                <div class="modal-body">
                    ${message}
                </div>
                <div class="modal-footer">
                    ${cancelText ? `<button class="btn btn-secondary modal-cancel">${cancelText}</button>` : ''}
                    <button class="btn btn-primary modal-confirm">${confirmText}</button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        document.body.classList.add('modal-open');
        this.currentModal = overlay;

        // Event handlers
        const confirmBtn = overlay.querySelector('.modal-confirm');
        const cancelBtn = overlay.querySelector('.modal-cancel');
        const closeBtn = overlay.querySelector('.modal-close');

        const handleConfirm = () => {
            if (onConfirm) onConfirm();
            this.close();
        };

        const handleCancel = () => {
            if (onCancel) onCancel();
            this.close();
        };

        confirmBtn.addEventListener('click', handleConfirm);
        if (cancelBtn) cancelBtn.addEventListener('click', handleCancel);
        closeBtn.addEventListener('click', handleCancel);

        if (closeOnOverlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    handleCancel();
                }
            });
        }

        // Keyboard support
        const handleKeyboard = (e) => {
            if (e.key === 'Escape') {
                handleCancel();
            } else if (e.key === 'Enter' && !cancelBtn) {
                handleConfirm();
            }
        };

        document.addEventListener('keydown', handleKeyboard);
        overlay.dataset.keyboardHandler = 'attached';

        return overlay;
    }

    close() {
        if (!this.currentModal) return;

        this.currentModal.classList.add('hiding');
        
        setTimeout(() => {
            if (this.currentModal) {
                this.currentModal.remove();
                document.body.classList.remove('modal-open');
                this.currentModal = null;
            }
        }, 200);
    }

    alert(message, title = 'Alert', type = 'info') {
        return new Promise((resolve) => {
            this.show({
                title,
                message,
                type,
                confirmText: 'OK',
                onConfirm: resolve
            });
        });
    }

    confirm(message, title = 'Confirm', type = 'warning') {
        return new Promise((resolve) => {
            this.show({
                title,
                message,
                type,
                confirmText: 'Confirm',
                cancelText: 'Cancel',
                onConfirm: () => resolve(true),
                onCancel: () => resolve(false)
            });
        });
    }

    success(message, title = 'Success') {
        return this.alert(message, title, 'success');
    }

    error(message, title = 'Error') {
        return this.alert(message, title, 'error');
    }

    warning(message, title = 'Warning') {
        return this.alert(message, title, 'warning');
    }

    info(message, title = 'Information') {
        return this.alert(message, title, 'info');
    }
}

// Create global instance
window.modal = new ModalManager();

// Override default alert with modal
window.alertOriginal = window.alert;
window.alert = (message) => {
    window.modal.alert(message);
};

// Override default confirm with modal
window.confirmOriginal = window.confirm;
window.confirm = (message) => {
    return window.modal.confirm(message);
};
