// Run the javascript code after the HTML document has been completely parsed,
//  and all deferred scripts (<script defer src="…"> and <script type="module">) have downloaded and executed.
document.addEventListener('DOMContentLoaded', function() {

    // Confirmation popup for deleting transactions
    let delete_button = document.querySelector("#delete_button");
    delete_button.addEventListener("click", function delete_transaction(event) {
        alert("javascript run")
        event.preventDefault();
        if (confirm('Do you want to submit?')) 
        {
            delete_button.click();
        } 
        else 
        {
            return false;
        }
    });
});





