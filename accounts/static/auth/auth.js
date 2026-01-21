function togglePasswords() {
    const pass1 = document.getElementById("password1");
    const pass2 = document.getElementById("password2");

    const type = pass1.type === "password" ? "text" : "password";

    pass1.type = type;
    pass2.type = type;

    document.querySelectorAll(".toggle-pass i").forEach(icon => {
        if (type === "text") {
            icon.classList.remove("bi-eye-slash-fill");
            icon.classList.add("bi-eye-fill");
        } else {
            icon.classList.remove("bi-eye-fill");
            icon.classList.add("bi-eye-slash-fill");
        }
    });
}



/* ------------------------------ */
/*  OCULTAR ERRORES DESPUÉS DE 5S */
/* ------------------------------ */
function hideErrorsAfterDelay() {
    const errors = document.querySelectorAll(".error, .field-error");

    if (errors.length === 0) return;

    setTimeout(() => {
        errors.forEach(el => {
            el.style.transition = "opacity 0.4s ease";
            el.style.opacity = "0";

            setTimeout(() => {
                el.remove();
            }, 400);
        });
    }, 5000);
}

/* ------------------------------ */
/*  INICIALIZAR EVENTOS EN FORM   */
/* ------------------------------ */
function initAuthJS() {
    document.querySelectorAll(".toggle-pass").forEach(el => {
        el.removeEventListener("click", togglePasswords);
        el.addEventListener("click", togglePasswords);
    });

    hideErrorsAfterDelay();
    initLiveValidation(); // 👈 ESTO ES LO QUE FALTABA
}

/* ------------------------------ */
/*  HTMX: SE EJECUTA CUANDO SE REEMPLAZA EL FORM  */
/* ------------------------------ */
document.addEventListener("htmx:afterSwap", function(evt) {
    if (evt.detail.target.id === "auth-form") {
        initAuthJS();
    }
});

/* ------------------------------ */
/*  CUANDO CARGA LA PÁGINA POR PRIMERA VEZ   */
/* ------------------------------ */
document.addEventListener("DOMContentLoaded", initAuthJS);


/* ------------------------------ */
/*  VALIDACIÓN EN TIEMPO REAL     */
/* ------------------------------ */
/* ------------------------------
/* ------------------------------
   TOGGLE PASSWORD
------------------------------ */

/* ------------------------------
   TOGGLE PASSWORD
------------------------------ */
function togglePasswords() {
    const inputs = document.querySelectorAll("#password1, #password2");
    const type = inputs[0].type === "password" ? "text" : "password";

    inputs.forEach(i => i.type = type);

    document.querySelectorAll(".toggle-pass i").forEach(icon => {
        icon.className = type === "text"
            ? "bi bi-eye-fill"
            : "bi bi-eye-slash-fill";
    });
}

/* ------------------------------
   HINT HELPER
------------------------------ */
function setHint(input, hint, isValid, message) {
    if (!input.value) {
        hint.textContent = "";
        hint.className = "field-hint";
        input.classList.remove("valid", "invalid");
        return;
    }

    hint.textContent = (isValid ? "✔ " : "✖ ") + message;
    hint.className = "field-hint active " + (isValid ? "success" : "error");

    input.classList.toggle("valid", isValid);
    input.classList.toggle("invalid", !isValid);
}

/* ------------------------------
   CHECK AVAILABILITY
------------------------------ */
function checkAvailability(field, value, input, hint) {
    fetch(`/accounts/check-availability/?field=${field}&value=${encodeURIComponent(value)}`)
        .then(r => r.json())
        .then(data => {
            if (data.exists) {
                setHint(input, hint, false,
                    field === "username"
                        ? "Usuario ya registrado"
                        : "Correo ya registrado"
                );
            }
            updateSubmitState();
        });
}

/* ------------------------------
   VALIDACIÓN EN TIEMPO REAL
------------------------------ */
function initLiveValidation() {
    const submitBtn = document.getElementById("submit-btn");

    const rules = {
        first_name: [/^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,30}$/, "Solo letras (2–30)"],
        last_name:  [/^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,30}$/, "Solo letras (2–30)"],
        username:   [/^[a-zA-Z0-9_]{4,20}$/, "4–20 caracteres"],
        email:      [/^[^\s@]+@[^\s@]+\.[^\s@]+$/, "Correo válido"],
        password1:  [/^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/,
                      "Mín. 8, mayúscula, número y símbolo"]
    };

    Object.entries(rules).forEach(([field, [regex, msg]]) => {
        const input = document.getElementById(field);
        const hint = document.getElementById(field + "Hint") ||
                     document.getElementById(field === "first_name" ? "firstNameHint" :
                                              field === "last_name" ? "lastNameHint" :
                                              "passwordHint");

        if (!input || !hint) return;

        input.addEventListener("input", () => {
            const ok = regex.test(input.value);
            setHint(input, hint, ok, msg);

            if (ok && (field === "username" || field === "email")) {
                checkAvailability(field, input.value, input, hint);
            }
            updateSubmitState();
        });
    });

    /* CONFIRMAR PASSWORD */
    const p1 = document.getElementById("password1");
    const p2 = document.getElementById("password2");
    const h2 = document.getElementById("password2Hint");

    p2.addEventListener("input", () => {
        setHint(p2, h2, p2.value === p1.value, "Las contraseñas coinciden");
        updateSubmitState();
    });

    function updateSubmitState() {
        submitBtn.disabled = document.querySelector(".invalid") !== null;
    }

    /* VALIDAR CAMPOS YA RELLENOS */
    document.querySelectorAll("input").forEach(i => {
        if (i.value) i.dispatchEvent(new Event("input"));
    });
}

/* ------------------------------
   BLOQUEAR ENTER
------------------------------ */
function blockEnterKey() {
    const form = document.querySelector(".register-form");

    form.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
        }
    });
}

/* ------------------------------
   INIT
------------------------------ */
function initAuthJS() {
    document.querySelectorAll(".toggle-pass")
        .forEach(el => el.onclick = togglePasswords);

    initLiveValidation();
    blockEnterKey();
}

document.addEventListener("DOMContentLoaded", initAuthJS);

document.addEventListener("htmx:afterSwap", e => {
    if (e.detail.target.id === "auth-form") initAuthJS();
});
