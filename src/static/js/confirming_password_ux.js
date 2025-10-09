const pw  = document.querySelector("input[name='password']");
const pw2 = document.querySelector("input[name='confirm_password']");
const icon = document.querySelector(".pw-status-icon");

if (pw && pw2 && icon) {
    function validateMatch() {
        if (!pw2.value) {
        icon.textContent = "";
        pw2.setCustomValidity("");
        pw2.classList.remove("valid-input", "invalid-input");
        return;
        }

        if (pw.value === pw2.value) {
        icon.textContent = "✓";
        icon.classList.add("valid");
        icon.classList.remove("invalid");
        pw2.setCustomValidity("");
        pw2.classList.add("valid-input");
        pw2.classList.remove("invalid-input");
        } 

        else {
        icon.textContent = "✗";
        icon.classList.add("invalid");
        icon.classList.remove("valid");
        pw2.setCustomValidity("Passwords do not match.");
        pw2.classList.add("invalid-input");
        pw2.classList.remove("valid-input");
        }
    }

    pw.addEventListener("input", validateMatch);
    pw2.addEventListener("input", validateMatch);
}