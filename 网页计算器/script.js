document.addEventListener('DOMContentLoaded', () => {
    const display = document.getElementById('display');
    const buttons = document.querySelectorAll('.buttons button');
    const historyList = document.getElementById('history-list');
    let history = [];

    // Button click event
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const value = button.getAttribute('data-value');
            if (value === '=') {
                calculate();
            } else if (value === 'C') {
                clearDisplay();
            } else {
                appendToDisplay(value);
            }
        });
    });

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        const key = e.key;
        if (/[0-9+\-*/.=]/.test(key)) {
            if (key === '=' || key === 'Enter') {
                calculate();
            } else {
                appendToDisplay(key);
            }
        } else if (key === 'Backspace') {
            clearDisplay();
        }
    });

    function appendToDisplay(value) {
        display.value += value;
    }

    function clearDisplay() {
        display.value = '';
    }

    function calculate() {
        try {
            const result = eval(display.value);
            display.value = result;
            addToHistory(`${display.value} = ${result}`);
        } catch (e) {
            display.value = 'Error';
        }
    }

    function addToHistory(entry) {
        history.push(entry);
        if (history.length > 10) history.shift(); // Limit history to 10 entries
        updateHistory();
    }

    function updateHistory() {
        historyList.innerHTML = history.map(entry => `<li>${entry}</li>`).join('');
    }
});

function toggleTheme() {
    const body = document.body;
    body.setAttribute('data-theme', body.getAttribute('data-theme') === 'dark' ? '' : 'dark');
}