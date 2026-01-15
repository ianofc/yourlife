
document.addEventListener('alpine:init', () => {
    Alpine.data('themeEngine', () => ({
        drawers: {
            talkio: false,
            notif: false,
            profile: false,
            theme: false,
            a11y: false
        },
        activeTheme: localStorage.getItem('niocortex_theme') || 'theme-aurora',
        accessModes: JSON.parse(localStorage.getItem('niocortex_access') || '[]'),

        init() {
            this.applyTheme(this.activeTheme);
            this.accessModes.forEach(mode => document.body.classList.add(mode));
        },

        toggleDrawer(name) {
            const wasOpen = this.drawers[name];
            Object.keys(this.drawers).forEach(k => this.drawers[k] = false);
            if (!wasOpen) this.drawers[name] = true;
        },

        setTheme(themeName) {
            this.activeTheme = themeName;
            localStorage.setItem('niocortex_theme', themeName);
            this.applyTheme(themeName);
        },

        applyTheme(themeName) {
            document.body.classList.remove('theme-aurora', 'theme-male-dark', 'theme-female-dark', 'theme-male-premium', 'theme-female-premium');
            document.body.classList.add(themeName);
        },

        toggleAccess(mode) {
            if (this.accessModes.includes(mode)) {
                this.accessModes = this.accessModes.filter(m => m !== mode);
                document.body.classList.remove(mode);
            } else {
                this.accessModes.push(mode);
                document.body.classList.add(mode);
            }
            localStorage.setItem('niocortex_access', JSON.stringify(this.accessModes));
        }
    }));
});
