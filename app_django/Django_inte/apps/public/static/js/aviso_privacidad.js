let privacyScrollPosition = 0;

function openPrivacyModal() {
    const modal = document.getElementById('privacyModal');
    modal.style.display = 'flex';

    privacyScrollPosition = window.pageYOffset || document.documentElement.scrollTop;

    document.body.style.position = 'fixed';
    document.body.style.top = `-${privacyScrollPosition}px`;
    document.body.style.width = '100%';
}

function closePrivacyModal() {
    const modal = document.getElementById('privacyModal');
    modal.style.display = 'none';

    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';

    window.scrollTo(0, privacyScrollPosition);
}

// Cerrar al hacer click fuera del contenedor blanco
document.addEventListener('click', function(e) {
    const modal = document.getElementById('privacyModal');
    if (modal && e.target === modal) closePrivacyModal();
});