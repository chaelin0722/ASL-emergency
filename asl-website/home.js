// i moved all the search functionality into a separate js file so that if we need to change it we only need to modify one file

document.addEventListener('DOMContentLoaded', () => {
    // 테스트 관련 로컬 스토리지 초기화
    const resetKeys = ["terms", "currentIndex", "reviewTerms", "wasCorrect", "testedTerm"];
    resetKeys.forEach(key => localStorage.removeItem(key));
    console.log("Clean local storage");

    // handle checkbox enabling/disabling
    const buttonItems = document.querySelectorAll('.btn-item'); // gets buttons on home page (under class 'btn-item')

    buttonItems.forEach((item, index) => {
        const checkbox1 = item.querySelector('.checkbox-1'); // "viewed"
        const checkbox2 = item.querySelector('.checkbox-2'); // "tested"

        const button = item.querySelector('.btn');

        if (!button || !checkbox1) return; // makes sure both checkbox + button exist

        const storageKey = `visited-${index}`; // local storage key to track state

        if (localStorage.getItem(storageKey) === 'visited') {
            checkbox1.checked = true;
        }

        button.addEventListener('click', function() {
            checkbox1.checked = true; // enable viewed button when viewed button is checked
            localStorage.setItem(storageKey, 'visited'); // local storage of state
        });
        
        checkbox1.addEventListener('change', () => {
            if (checkbox1.checked) {
                checkbox2.disabled = false; // enable tested button when viewed button is checked
            } else {
                checkbox2.disabled = true; // disable tested button when viewed button is unchecked
                checkbox2.checked = false; // uncheck tested button when disabled
            }
        });
    });

    // button click handling for page navigation
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // generate a URL based on the button title, replace spaces with hyphens
            console.log("button clicked!");
            const title = button.getAttribute('data-title');
            if (title) {
                const pageTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, '-') + '.html';
                window.location.href = pageTitle;
            }
        });
    });

    console.log("Page loaded, script running...");

    const resetButton = document.getElementById('reset-btn');
    if (!resetButton) {
        console.error("Reset button not found!");
    }
    else{
        console.log("reset found!")
    }

    resetButton.addEventListener("click", function() {
        localStorage.clear();
        document.querySelectorAll('.checkbox-1').forEach(checkbox => {
            checkbox.checked = false;
        });
    });
});