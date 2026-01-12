// Black-themed Toast Notification System
class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = new Set();
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    show(message, type = 'info', title = null, duration = 5000) {
        const toast = this.createToast(message, type, title, duration);
        this.container.appendChild(toast);
        this.toasts.add(toast);

        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => this.dismiss(toast), duration);
        }

        return toast;
    }

    createToast(message, type, title, duration) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const defaultTitles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };

        const icon = icons[type] || icons.info;
        const toastTitle = title || defaultTitles[type] || defaultTitles.info;

        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-title">${toastTitle}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Close">&times;</button>
            ${duration > 0 ? `<div class="toast-progress"><div class="toast-progress-bar" style="animation-duration: ${duration}ms;"></div></div>` : ''}
        `;

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.dismiss(toast));

        return toast;
    }

    dismiss(toast) {
        if (!this.toasts.has(toast)) return;

        toast.classList.add('hiding');
        setTimeout(() => {
            toast.remove();
            this.toasts.delete(toast);
        }, 300);
    }

    success(message, title = null, duration = 5000) {
        return this.show(message, 'success', title, duration);
    }

    error(message, title = null, duration = 7000) {
        return this.show(message, 'error', title, duration);
    }

    warning(message, title = null, duration = 6000) {
        return this.show(message, 'warning', title, duration);
    }

    info(message, title = null, duration = 5000) {
        return this.show(message, 'info', title, duration);
    }

    clear() {
        this.toasts.forEach(toast => this.dismiss(toast));
    }
}

// Create global instance
window.toast = new ToastManager();

// Helper function for backward compatibility
window.showToast = (message, type = 'info', title = null, duration = 5000) => {
    return window.toast.show(message, type, title, duration);
};
