let scrollPosition = 0;

function openContactModal() {
    const modal = document.getElementById('contactModal');
    modal.style.display = 'flex';
    scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    document.body.style.position = 'fixed';
    document.body.style.top = `-${scrollPosition}px`;
    document.body.style.width = '100%';
}

function closeContactModal() {
    const modal = document.getElementById('contactModal');
    modal.style.display = 'none';
    document.body.style.position = '';
    document.body.style.top = '';
    window.scrollTo(0, scrollPosition);
}

function copyEmail(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const tooltip = button.querySelector('.tooltip');
        const originalText = tooltip.innerText;
        tooltip.innerText = "¡Copiado!";
        tooltip.style.opacity = "1";
        
        setTimeout(() => {
            tooltip.style.opacity = "0";
            setTimeout(() => tooltip.innerText = "¡Copiar!", 300);
        }, 1500);
    });
}

document.addEventListener('click', function(e) {
    const modal = document.getElementById('contactModal');
    if (modal && e.target === modal) closeContactModal();
});