(function () {
    const list = document.getElementById("sent-invitations-list");
    if (!list) {
        return;
    }

    const companyId = list.dataset.companyId;
    if (!companyId) {
        return;
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${protocol}://${window.location.host}/ws/companies/${companyId}/invitations/`;
    const reconnectBaseMs = 1500;
    const reconnectMaxMs = 30000;
    let reconnectAttempts = 0;
    let reconnectTimer = null;

    function escapeHtml(value) {
        return String(value || "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function removeEmptyState() {
        const empty = document.getElementById("sent-invitations-empty");
        if (empty) {
            empty.remove();
        }
    }

    function getRow(invitationId) {
        return list.querySelector(`[data-invitation-id="${invitationId}"]`);
    }

    function setStatusChip(chip, status, statusDisplay) {
        if (!chip) {
            return;
        }

        chip.classList.remove("pending", "accepted", "rejected", "cancelled");
        chip.classList.add(status);
        chip.textContent = statusDisplay;
    }

    function createRow(invitation) {
        const row = document.createElement("li");
        row.className = "invitation-row";
        row.dataset.invitationId = String(invitation.id);
        row.innerHTML = `
            <span class="user">${escapeHtml(invitation.invited_user_username)}</span>
            <span class="user-email">${escapeHtml(invitation.invited_user_email)}</span>
            <span class="status invitation-status-right ${escapeHtml(invitation.status)}">${escapeHtml(invitation.status_display)}</span>
        `;
        return row;
    }

    function upsertInvitation(invitation) {
        if (!invitation || !invitation.id) {
            return;
        }

        removeEmptyState();
        const existingRow = getRow(invitation.id);
        if (!existingRow) {
            list.prepend(createRow(invitation));
            return;
        }

        const statusChip = existingRow.querySelector(".status");
        setStatusChip(statusChip, invitation.status, invitation.status_display);
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
                if (payload.type === "invitation.status_updated") {
                    upsertInvitation(payload.invitation);
                }
            } catch (error) {
                console.error("No se pudo procesar el estado de invitacion:", error);
            }
        };

        socket.onerror = function () {
            socket.close();
        };

        socket.onclose = function (event) {
            if (event.code === 4401 || event.code === 4403) {
                return;
            }
            scheduleReconnect();
        };
    }

    connect();
})();
