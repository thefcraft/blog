// Function to add dark mode stylesheet
function addDarkMode() {
    let head = document.getElementsByTagName('HEAD')[0];
    let link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = '/static/css/darkmode.css';
    link.id = 'dark-mode-stylesheet';  // Adding an id for easy removal
    head.appendChild(link);
}

// Function to remove dark mode stylesheet
function removeDarkMode() {
    let darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    if (darkModeStylesheet) {
        darkModeStylesheet.parentNode.removeChild(darkModeStylesheet);
    }
}

function isDarkMode() {
    let darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    if (darkModeStylesheet) {
        return true;
    }
    return false;
}

function changeTheme(elem) {
    if(document.getElementById('dark-mode-stylesheet')){
        removeDarkMode();
    }else{
        addDarkMode();
    }   
}
