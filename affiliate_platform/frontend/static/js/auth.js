/**
 * Утилиты для управления авторизацией
 */

// Проверка авторизации
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');

    return {
        isAuthenticated: !!(token && user),
        token,
        user
    };
}

// Обновление навигации в зависимости от статуса авторизации
function updateNavigation() {
    const auth = checkAuth();
    const navbar = document.querySelector('.navbar-nav');

    if (!navbar) return;

    if (auth.isAuthenticated) {
        // Пользователь авторизован
        navbar.innerHTML = `
            <li><a href="/">Главная</a></li>
            <li><a href="/offers">Офферы</a></li>
            <li><a href="/dashboard">Кабинет</a></li>
            <li><a href="#" id="userNameNav">${auth.user.full_name || auth.user.email}</a></li>
            <li><a href="#" id="logoutBtn" class="btn btn-primary">Выйти</a></li>
        `;

        // Добавляем обработчик выхода
        document.getElementById('logoutBtn').addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    } else {
        // Пользователь не авторизован
        navbar.innerHTML = `
            <li><a href="/">Главная</a></li>
            <li><a href="/offers">Офферы</a></li>
            <li><a href="/login">Войти</a></li>
            <li><a href="/register" class="btn btn-primary">Регистрация</a></li>
        `;
    }
}

// Выход из системы
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Проверка токена на валидность
function isTokenValid(token) {
    if (!token) return false;

    try {
        // Декодируем JWT токен (без проверки подписи на клиенте)
        const payload = JSON.parse(atob(token.split('.')[1]));
        const exp = payload.exp * 1000; // Конвертируем в миллисекунды

        return Date.now() < exp;
    } catch (e) {
        return false;
    }
}

// Проверка и обновление токена при загрузке страницы
function initAuth() {
    const auth = checkAuth();

    // Проверяем валидность токена
    if (auth.isAuthenticated && !isTokenValid(auth.token)) {
        console.log('Токен истёк, выход из системы');
        logout();
        return;
    }

    // Обновляем навигацию
    updateNavigation();
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        checkAuth,
        updateNavigation,
        logout,
        isTokenValid,
        initAuth
    };
}
