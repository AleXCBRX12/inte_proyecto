let devScrollPos = 0;

function openDevelopersModal() {
    const modal = document.getElementById("developersModal");
    if(!modal) return;
    modal.style.display = "flex";

    devScrollPos = window.pageYOffset || document.documentElement.scrollTop;
    document.body.style.position = "fixed";
    document.body.style.top = `-${devScrollPos}px`;
    document.body.style.width = '100%';
}

function closeDevelopersModal() {
    const modal = document.getElementById("developersModal");
    if(!modal) return;
    modal.style.display = "none";

    document.body.style.position = '';
    document.body.style.top = '';
    window.scrollTo(0, devScrollPos);
}

window.addEventListener('click', function(e) {
    const modal = document.getElementById("developersModal");
    if(modal && e.target === modal){
        closeDevelopersModal();
    }
});