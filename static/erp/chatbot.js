document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("iaChatbot");
    if (!root) return;

    const desktopToggle = document.getElementById("iaChatbotToggle");
    const mobileToggle = document.querySelector(".ia-chatbot-mobile-trigger");
    const closeBtn = document.getElementById("iaChatbotClose");
    const panel = document.getElementById("iaChatbotPanel");
    const form = document.getElementById("iaChatbotForm");
    const input = document.getElementById("iaChatbotInput");
    const messagesBox = document.getElementById("iaChatbotMessages");
    const streamUrl = root.dataset.streamUrl || root.dataset.chatUrl;
    const csrfInput = form ? form.querySelector('input[name="csrfmiddlewaretoken"]') : null;
    const history = [];

    if (!panel || !form || !input || !messagesBox || !streamUrl) return;

    function setExpanded(isOpen) {
        root.classList.toggle("open", isOpen);
        panel.setAttribute("aria-hidden", String(!isOpen));
        if (desktopToggle) desktopToggle.setAttribute("aria-expanded", String(isOpen));
        if (mobileToggle) {
            mobileToggle.setAttribute("aria-expanded", String(isOpen));
            mobileToggle.classList.toggle("active", isOpen);
        }
        if (isOpen) {
            window.setTimeout(() => input.focus(), 80);
        }
    }

    function closeChat() {
        setExpanded(false);
    }

    function toggleChat(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        setExpanded(!root.classList.contains("open"));
    }

    function renderMessageContent(element, content) {
        const normalized = (content || "")
            .replace(/^[ \t]*[*-][ \t]+/gm, "\u2022 ")
            .replace(/^[ \t]*\u2022[ \t]+/gm, "\u2022 ");

        const html = normalized
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/^\u2022\s+(.+)$/gm, "<span class=\"ia-bullet\">\u2022 $1</span>")
            .replace(/\n/g, "<br>");

        element.innerHTML = html;
    }

    function appendMessage(content, type) {
        const message = document.createElement("div");
        message.className = `ia-message ia-message-${type}`;
        renderMessageContent(message, content);
        messagesBox.appendChild(message);
        messagesBox.scrollTop = messagesBox.scrollHeight;
        return message;
    }

    function renderChart(target, chart) {
        if (!chart || !Array.isArray(chart.labels) || !Array.isArray(chart.series)) return;

        const existing = target.querySelector(".ia-chart");
        if (existing) existing.remove();

        const chartBox = document.createElement("div");
        chartBox.className = "ia-chart";

        const title = document.createElement("div");
        title.className = "ia-chart-title";
        title.textContent = chart.title || "Grafica del sistema";
        chartBox.appendChild(title);

        if (chart.description) {
            const description = document.createElement("div");
            description.className = "ia-chart-description";
            description.textContent = chart.description;
            chartBox.appendChild(description);
        }

        const allValues = chart.series.reduce((values, serie) => {
            if (Array.isArray(serie.values)) values.push(...serie.values);
            return values;
        }, []);
        const maxValue = Math.max(1, ...allValues);

        chart.labels.forEach((label, index) => {
            const row = document.createElement("div");
            row.className = "ia-chart-row";

            const labelEl = document.createElement("div");
            labelEl.className = "ia-chart-label";
            labelEl.textContent = label;
            row.appendChild(labelEl);

            chart.series.forEach((serie) => {
                const value = Number((serie.values || [])[index] || 0);
                const item = document.createElement("div");
                item.className = "ia-chart-item";

                const meta = document.createElement("div");
                meta.className = "ia-chart-meta";
                meta.innerHTML = `<span>${serie.label}</span><strong>${value}</strong>`;

                const track = document.createElement("div");
                track.className = "ia-chart-track";

                const bar = document.createElement("div");
                bar.className = "ia-chart-bar";
                bar.style.width = `${Math.max(4, (value / maxValue) * 100)}%`;
                bar.style.background = serie.color || "#006130";

                track.appendChild(bar);
                item.appendChild(meta);
                item.appendChild(track);
                row.appendChild(item);
            });

            if (Array.isArray(chart.totals)) {
                const total = document.createElement("div");
                total.className = "ia-chart-total";
                total.textContent = `Total: ${Number(chart.totals[index] || 0)}`;
                row.appendChild(total);
            }

            chartBox.appendChild(row);
        });

        target.appendChild(chartBox);
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    function setLoading(isLoading) {
        input.disabled = isLoading;
        const submit = form.querySelector(".ia-chatbot-send");
        if (submit) submit.disabled = isLoading;
    }

    function getCookie(name) {
        const cookies = document.cookie ? document.cookie.split(";") : [];
        for (const cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(`${name}=`)) {
                return decodeURIComponent(trimmed.slice(name.length + 1));
            }
        }
        return "";
    }

    function createWordRenderer(target) {
        let pending = "";
        let visible = "";
        let done = false;
        let timer = null;
        let finishResolver = null;

        function nextPiece() {
            const match = pending.match(/^(\s*\S+\s+)/);
            if (match) {
                pending = pending.slice(match[1].length);
                return match[1];
            }
            if (done && pending) {
                const rest = pending;
                pending = "";
                return rest;
            }
            return "";
        }

        function tick() {
            const piece = nextPiece();
            if (piece) {
                visible += piece;
                renderMessageContent(target, `${visible}\u258C`);
                messagesBox.scrollTop = messagesBox.scrollHeight;
                return;
            }

            if (done) {
                window.clearInterval(timer);
                timer = null;
                renderMessageContent(target, visible);
                if (finishResolver) {
                    finishResolver();
                    finishResolver = null;
                }
            }
        }

        return {
            push(text) {
                pending += text;
                if (!timer) {
                    timer = window.setInterval(tick, 42);
                }
            },
            finish() {
                done = true;
                if (!timer) {
                    timer = window.setInterval(tick, 42);
                }
                return new Promise((resolve) => {
                    finishResolver = resolve;
                });
            },
        };
    }

    async function sendMessageStream(message, target) {
        const response = await fetch(streamUrl, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfInput && csrfInput.value ? csrfInput.value : getCookie("csrftoken"),
            },
            body: JSON.stringify({
                message,
                history,
            }),
        });

        if (!response.ok || !response.body) {
            const data = await response.json().catch(() => ({
                message: `Respuesta inesperada del servidor (${response.status}).`,
            }));
            const detail = data.detail ? ` ${data.detail}` : "";
            throw new Error(`${data.message || "Pallet no pudo responder ahora."}${detail}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const renderer = createWordRenderer(target);
        let buffer = "";
        let answer = "";
        let chart = null;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split("\n\n");
            buffer = events.pop() || "";

            for (const event of events) {
                const line = event.split("\n").find((item) => item.startsWith("data:"));
                if (!line) continue;

                const rawData = line.replace(/^data:\s*/, "");
                if (rawData === "[DONE]") {
                    await renderer.finish();
                    return { answer, chart };
                }

                const data = JSON.parse(rawData);
                if (data.error) {
                    throw new Error(data.detail ? `${data.error} ${data.detail}` : data.error);
                }

                if (data.token) {
                    answer += data.token;
                    renderer.push(data.token);
                }

                if (data.chart) {
                    chart = data.chart;
                }
            }
        }

        await renderer.finish();
        if (!answer.trim()) {
            throw new Error("Pallet no devolvio contenido.");
        }

        return { answer, chart };
    }

    if (desktopToggle) desktopToggle.addEventListener("click", toggleChat);
    if (mobileToggle) mobileToggle.addEventListener("click", toggleChat);
    if (closeBtn) closeBtn.addEventListener("click", closeChat);

    input.addEventListener("input", () => {
        input.style.height = "auto";
        input.style.height = `${Math.min(input.scrollHeight, 108)}px`;
    });

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            form.requestSubmit();
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        appendMessage(message, "user");
        history.push({ role: "user", content: message });
        input.value = "";
        input.style.height = "auto";
        setLoading(true);

        const assistantMessage = appendMessage("", "assistant ia-message-thinking");

        try {
            const result = await sendMessageStream(message, assistantMessage);
            const answer = result.answer || "";
            assistantMessage.classList.remove("ia-message-streaming");
            assistantMessage.classList.remove("ia-message-thinking");
            window.setTimeout(() => {
                renderMessageContent(assistantMessage, answer);
                renderChart(assistantMessage, result.chart);
            }, 90);
            history.push({ role: "assistant", content: answer });
            while (history.length > 10) history.shift();
        } catch (error) {
            assistantMessage.remove();
            appendMessage(error.message, "error");
        } finally {
            setLoading(false);
            input.focus();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && root.classList.contains("open")) {
            closeChat();
        }
    });
});
