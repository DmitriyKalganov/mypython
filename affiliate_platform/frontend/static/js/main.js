/**
 * Основные функции для партнёрской платформы
 */

// Утилиты для работы с API
const api = {
    baseUrl: '',

    async request(endpoint, options = {}) {
        const token = localStorage.getItem('token');

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(this.baseUrl + endpoint, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Ошибка запроса');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint);
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};

// Форматирование чисел
function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU').format(price);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Копирование в буфер обмена
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Скопировано в буфер обмена!', 'success');
        });
    } else {
        // Fallback для старых браузеров
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('Скопировано в буфер обмена!', 'success');
    }
}

// Уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Проверка авторизации
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    return {
        isAuthenticated: !!token && !!user.id,
        user,
        token
    };
}

// Выход из системы
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Валидация форм
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = 'var(--danger-color)';
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    });

    return isValid;
}

// Дебаунс для поиска
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Загрузка данных с индикатором
async function loadWithSpinner(element, loadFunction) {
    element.innerHTML = '<p style="text-align: center;">⏳ Загрузка...</p>';

    try {
        await loadFunction();
    } catch (error) {
        element.innerHTML = '<p style="text-align: center; color: var(--danger-color);">Ошибка загрузки данных</p>';
        console.error('Load error:', error);
    }
}

// Работа с модальными окнами
class Modal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.closeBtn = this.modal.querySelector('.modal-close');

        this.closeBtn?.addEventListener('click', () => this.close());

        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
    }

    open() {
        this.modal.classList.add('active');
    }

    close() {
        this.modal.classList.remove('active');
    }
}

// Анимации появления
function animateOnScroll() {
    const elements = document.querySelectorAll('.fade-in');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.animation = 'fadeIn 0.5s ease-out forwards';
            }
        });
    });

    elements.forEach(element => observer.observe(element));
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    animateOnScroll();

    // Автоматическое скрытие алертов
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        api,
        formatPrice,
        formatDate,
        copyToClipboard,
        showNotification,
        checkAuth,
        logout,
        validateForm,
        debounce,
        loadWithSpinner,
        Modal
    };
}
