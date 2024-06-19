let is_already_speaking = false;
function speak() {
    
    if (is_already_speaking){
        speechSynthesis.cancel();
        is_already_speaking = false;
        document.querySelector('#speak-nav').innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M3 12a9 9 0 1 1 18 0 9 9 0 0 1-18 0zm9-10a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm3.38 10.42l-4.6 3.06a.5.5 0 0 1-.78-.41V8.93c0-.4.45-.63.78-.41l4.6 3.06c.3.2.3.64 0 .84z" fill="currentColor"></path>
        </svg>`;
    }else{
        const contentElement = document.querySelector('#content');
        const tagsElement = document.querySelector('#tag-footer');
        const reactionElement = document.querySelector('#reaction-footer');
        
        let textToSpeak = '';

        // Iterate through all child nodes of the content element
        contentElement.childNodes.forEach(node => {
            if (node !== tagsElement && node !== reactionElement) {
                textToSpeak += node.textContent.trim();
            }
        });

        const utterance = new SpeechSynthesisUtterance(textToSpeak);

        // Listen for the 'end' event
        utterance.onend = function() {
            is_already_speaking = false;
            document.querySelector('#speak-nav').innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M3 12a9 9 0 1 1 18 0 9 9 0 0 1-18 0zm9-10a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm3.38 10.42l-4.6 3.06a.5.5 0 0 1-.78-.41V8.93c0-.4.45-.63.78-.41l4.6 3.06c.3.2.3.64 0 .84z" fill="currentColor"></path>
            </svg>`;
        };


        speechSynthesis.speak(utterance);
        is_already_speaking = true;
        document.querySelector('#speak-nav').innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1" fill="none"/>
            <rect x="9" y="9" width="6" height="6" fill="currentColor"/>
        </svg>`;
    }
}

window.onload = () => {
    speechSynthesis.cancel();
};

function handel_share(event){
        // Fallback, Tries to use API only
        // if navigator.share function is
        // available
        const data = {
            title: document.title,
            text: document.querySelector('#blog-desc').innerHTML,
            url: document.location.href,
        };
        if (navigator.share) {
            navigator.share(data).then(() => {
                console.log('Thanks for sharing!');
            }).catch(err => {
                // Handle errors, if occurred
                console.log("Error while using Web share API:");
                console.log(err);
            });
        } else {
            // Alerts user if API not available 
            alert("Browser doesn't support this API !");
        }
}
document.querySelector('#share-nav').addEventListener('click', event => {handel_share(event);});
document.querySelector('#share-footer').addEventListener('click', event => {handel_share(event);});
document.querySelector('#speak-nav').addEventListener('click', event => {speak();});


const checkbox = document.getElementById("checkbox")
checkbox.checked = !isDarkMode();
checkbox.addEventListener("change", () => {
    localStorage.setItem('darkmode', !checkbox.checked);
    console.log("darkmode set to: ", !checkbox.checked);
    if (checkbox.checked) removeDarkMode();
    else addDarkMode();
})
let darkmode = localStorage.getItem('darkmode');
if (darkmode != null) {
    console.log(darkmode);
    if (darkmode==='true') {
        addDarkMode();
        checkbox.checked = false;
    }
}else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        addDarkMode();
        checkbox.checked = false;
}