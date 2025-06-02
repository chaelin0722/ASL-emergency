// array of available terms (stored separately, not displayed --> UPDATE AS WE GO)

import {terms} from './constants.js';

function search_term() {
    console.log('function started!');
    const input = document.getElementById('searchbar').value.toLowerCase(); // gets input from search bar
    const searchResults = document.getElementById('search-results'); // what's outputted in drop-down results

    searchResults.innerHTML = ''; // clear previous results
    searchResults.style.display = 'none'; // hide dropdown when you're not searching

    if (input.trim() === '') {
        return; // do nothing if input is empty
    }

    // filter terms based on what matches input (to be put in list below)
    const matches = terms.filter(item => item.term.toLowerCase().includes(input));

    // display matches in the dropdown
    matches.forEach(item => {
        const resultItem = document.createElement('li'); // creates list item
        resultItem.textContent = item.term;
        resultItem.onclick = () => {
            // redirects to video page with matching term (encodeURIComponent just handles special characters so it won't break)
            window.location.href = `video.html?term=${encodeURIComponent(item.term)}`;
        };
        searchResults.appendChild(resultItem);
    });

    // show dropdown if there are matches
    if (matches.length > 0) {
        searchResults.style.display = 'block';
    }
}

const searchbar = document.getElementById('searchbar');
searchbar.addEventListener('keyup', search_term);