/**
 * Desktop Notifications System
 */

class NotificationSystem {
    constructor() {
        this.enabled = false;
        this.permission = Notification.permission;

        this.init();
    }

    async init() {
        // Verificar suporte
        if (!("Notification" in window)) {
            return;
        }

        // NÃO pedir permissão automaticamente - apenas verificar se já foi concedida
        this.enabled = this.permission === "granted";

        if (this.enabled) {
            console.log('🔔 Notificações desktop disponíveis');
        }

        // Usuário pode ativar manualmente via:
        // window.notificationSystem.requestPermission()
    }

    notify(title, message, options = {}) {
        if (!this.enabled) return;

        // Não notificar se janela está em foco
        if (document.hasFocus()) return;

        const notification = new Notification(title, {
            body: message.substring(0, 100) + (message.length > 100 ? '...' : ''),
            icon: '💬',
            badge: '🤖',
            tag: 'claude-chat',
            requireInteraction: false,
            ...options
        });

        // Click na notificação = focar janela
        notification.onclick = () => {
            window.focus();
            notification.close();
        };

        // Auto-close após 5s
        setTimeout(() => notification.close(), 5000);

        window.debugSystem?.log('info', 'Notifications', `Notificação enviada: ${title}`);
    }

    notifyResponse(content) {
        const preview = content.substring(0, 80);
        this.notify(
            '🤖 Claude respondeu',
            preview,
            {
                icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="75" font-size="75">🤖</text></svg>'
            }
        );
    }

    notifyError(error) {
        this.notify(
            '❌ Erro no Chat',
            error,
            {
                icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="75" font-size="75">❌</text></svg>',
                requireInteraction: true
            }
        );
    }

    async requestPermission() {
        if (this.permission === "granted") {
            alert('✅ Notificações já estão ativadas!');
            return;
        }

        const result = await Notification.requestPermission();
        this.permission = result;
        this.enabled = result === "granted";

        if (this.enabled) {
            alert('✅ Notificações ativadas!');
            this.notify('🎉 Notificações Ativadas', 'Você receberá notificações quando Claude responder');
        } else {
            alert('❌ Permissão negada. Você não receberá notificações.');
        }
    }
}

// Notificações ativas silenciosamente (sem botão)
// Usuário pode ativar via navegador se quiser
console.log('🔔 Notificações disponíveis (aprove se quiser)');

// Inicializar
window.addEventListener('load', () => {
    window.notificationSystem = new NotificationSystem();
});
