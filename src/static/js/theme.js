(function () {
    const storageKey = 'studymorph-theme';
    const root = document.documentElement;

    function getTheme() {
        const saved = localStorage.getItem(storageKey);
        return saved === 'dark' || saved === 'light' ? saved : 'light';
    }

    function updateControls(theme) {
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            const isDark = theme === 'dark';
            button.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            button.setAttribute('title', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            button.setAttribute('aria-pressed', String(isDark));
            const icon = button.querySelector('[data-theme-icon]');
            if (icon) icon.textContent = isDark ? '\u2600' : '\u263e';
        });
    }

    function setTheme(theme) {
        root.setAttribute('data-theme', theme);
        localStorage.setItem(storageKey, theme);
        updateControls(theme);
    }

    root.setAttribute('data-theme', getTheme());

    document.addEventListener('DOMContentLoaded', () => {
        updateControls(root.getAttribute('data-theme'));
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            button.addEventListener('click', () => {
                setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
            });
        });
    });
}());