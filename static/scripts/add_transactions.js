// Run the javascript code after the HTML document has been completely parsed,
//  and all deferred scripts (<script defer src="…"> and <script type="module">) have downloaded and executed.
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');

    // If date input is empty
    if (!dateInput.value)
    {
        // Set default date to today using the user's timezone
        dateInput.value = formatDate();
    }

    // Convert date and month input to have 2 digits
    function padTo2Digits(num) {
        return num.toString().padStart(2, '0');
    }

    // Format the current date as YYYY-MM-DD
    function formatDate(date = new Date()) {
        return [
            date.getFullYear(),
            padTo2Digits(date.getMonth() + 1),
            padTo2Digits(date.getDate()),
        ].join('-');
    }
});





