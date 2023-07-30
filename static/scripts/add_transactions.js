// Run the javascript code after the HTML document has been completely parsed,
//  and all deferred scripts (<script defer src="…"> and <script type="module">) have downloaded and executed.
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');

    // Using the user's timezone
    dateInput.value = formatDate();

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


    // Validate user input for adding transactions
    let form = document.querySelector('add_transactions');
    form.addEventListener('submit', function validateForm() {
        // Get input data from the form
        const date = document.querySelector('date');
        const account = document.querySelector('account');
        const category = document.querySelector('category');
        const description = document.querySelector('description');
        const income = document.querySelector('income');
        const expense = document.querySelector('expense');

        return false;

        // If both income and expense inputs are empty
        if (income == "" || expense == "")
        {
            alert("Please specify income and/or expense");
            // e.preventDefault();
            return false;
        }
        
        if (account == "")
        {
            alert("Please specify account");
            return false;
        }

        if (income < 0 || expense < 0)
        {
            alert("income and expense must be nonnegative");
            return false;
        }

    });
});





