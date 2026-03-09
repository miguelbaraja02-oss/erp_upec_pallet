(function () {
    const list = document.getElementById("invitations-list");
    if (!list) {
        return;
    }

    const notificationDot = document.getElementById("notification-dot");
    const emptyStateId = "invitations-empty-state";
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${protocol}://${window.location.host}/ws/invitations/`;
    const csrfToken = list.dataset.csrfToken || getCookie("csrftoken");
    const reconnectBaseMs = 1500;
    const reconnectMaxMs = 30000;
    let reconnectAttempts = 0;
    let reconnectTimer = null;

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    }

    function showNotificationDot() {
        if (notificationDot) {
            notificationDot.classList.remove("d-none");
        }
    }

    function escapeHtml(value) {
        return String(value || "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function removeEmptyStateIfExists() {
        const emptyState = document.getElementById(emptyStateId);
        if (emptyState) {
            emptyState.remove();
        }
    }

    function invitationExists(invitationId) {
        return !!list.querySelector(`[data-invitation-id="${invitationId}"]`);
    }

    function buildCompanyAvatar(logoUrl) {
        if (logoUrl) {
            return `<img src="${escapeHtml(logoUrl)}" alt="Avatar empresa" class="company-avatar">`;
        }
        return '<i class="bi bi-building-fill company-avatar-icon"></i>';
    }

    function buildActionForm(actionUrl, actionClass, buttonClass, label) {
        const safeActionUrl = escapeHtml(actionUrl);
        return `
            <form method="post" action="${safeActionUrl}">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                <button type="submit" class="${actionClass} ${buttonClass}" style="border-radius:0;">${label}</button>
            </form>
        `;
    }

    function prependInvitationCard(invitation) {
        if (!invitation || invitationExists(invitation.id)) {
            return;
        }

        removeEmptyStateIfExists();
        showNotificationDot();

        const item = document.createElement("li");
        item.className = "invitation-card";
        item.dataset.invitationId = String(invitation.id);
        item.innerHTML = `
            <div class="invitation-header">
                ${buildCompanyAvatar(invitation.company_logo_url)}
                <span class="invitation-company">${escapeHtml(invitation.company_name)}</span>
            </div>
            <div class="invitation-by">Invitado por: <b>${escapeHtml(invitation.invited_by_username)}</b></div>
            <div class="invitation-actions">
                ${buildActionForm(invitation.accept_url, "accept", "btn-aceptar", "Aceptar")}
                ${buildActionForm(invitation.reject_url, "reject", "btn-rechazar", "Rechazar")}
            </div>
        `;

        list.prepend(item);
    }

    function scheduleReconnect() {
        if (reconnectTimer) {
            return;
        }

        const delay = Math.min(reconnectBaseMs * (2 ** reconnectAttempts), reconnectMaxMs);
        reconnectAttempts += 1;
        reconnectTimer = setTimeout(function () {
            reconnectTimer = null;
            connect();
        }, delay);
    }

    function connect() {
        const socket = new WebSocket(socketUrl);

        socket.onopen = function () {
            reconnectAttempts = 0;
        };

        socket.onmessage = function (event) {
            try {
                const payload = JSON.parse(event.data);
                if (payload.type === "invitation.created") {
                    prependInvitationCard(payload.invitation);
                }
            } catch (error) {
                console.error("No se pudo procesar el mensaje de invitaciones:", error);
            }
        };

        socket.onclose = function (event) {
            if (event.code === 4401 || event.code === 4403) {
                return;
            }
            scheduleReconnect();
        };

        socket.onerror = function () {
            socket.close();
        };
    }

    connect();
})();
