const checkIn  = document.querySelector("input[name='check_in']");
const checkOut = document.querySelector("input[name='check_out']");

if (checkIn && checkOut) {
    // Helper to always return two digits
    const twoDigit = (num) => String(num).padStart(2, "0");
    
    function applyCheckoutMin() {
        if (!checkIn.value) return;

        // Parses YYYY-MM-DD safely in local time
        const [y, m, d] = checkIn.value.split("-").map(Number);
        const nextDay = new Date(y, m - 1, d + 1);

        const minCheckout =
            `${nextDay.getFullYear()}-${twoDigit(nextDay.getMonth() + 1)}-${twoDigit(nextDay.getDate())}`;

        // Sets checkout’s earliest allowed date = day after check-in
        checkOut.min = minCheckout;

        // If current checkout is missing or earlier than allowed, fix it
        if (!checkOut.value || checkOut.value < minCheckout) {
            checkOut.value = minCheckout;
        }
    }

    // Updates when check-in changes
    checkIn.addEventListener("change", applyCheckoutMin);

    // Applies once on load (handles re-renders after errors)
    applyCheckoutMin();
}