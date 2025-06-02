document.addEventListener('DOMContentLoaded', () => {
    // handle checkbox enabling/disabling
    const buttonItems = document.querySelectorAll('.btn-item'); // gets buttons on home page (under class 'btn-item')

    buttonItems.forEach((item, index) => {
        const checkbox2 = item.querySelector('.checkbox-2'); // "tested"
        const button = item.querySelector('.btn');

        if (!button || !checkbox2) return; // makes sure both checkbox + button exist

        const storageKey = `visited-${index}`; // local storage key to track state

        if (localStorage.getItem(storageKey) === 'visited') {
            checkbox2.checked = true;
        }

        button.addEventListener('click', function() {
            checkbox2.checked = true; // enable tested button when viewed button is checked
            localStorage.setItem(storageKey, 'visited'); // local storage of state
        });
    });

    // button click handling for page navigation
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // generate a URL based on the button title, replace spaces with hyphens
            const title = button.getAttribute('data-title');
            const pageTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, '-') + '.html';
            window.location.href = pageTitle;
        });
    });

    console.log("Page loaded, script running...");

    const resetButton = document.getElementById('reset-btn');

    resetButton.addEventListener("click", function() {
        localStorage.clear();
        document.querySelectorAll('.checkbox-2').forEach(checkbox => {
            checkbox.checked = false;
        });
    });
});