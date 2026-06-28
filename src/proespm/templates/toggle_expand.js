function toggleLabBookView() {
    const btn = document.getElementById('lab-book-btn');
    const overview = document.getElementById('overview_root');
    const sections = [...document.querySelectorAll('section > details')];
    const entering = !btn.classList.contains('active');

    if (entering) {
        // Enter Lab Book View: everything starts collapsed
        document.body.classList.add('lab-book-view');
        overview.removeAttribute('open');
        sections.forEach(d => d.removeAttribute('open'));
        btn.classList.add('active');
    } else {
        // Exit Lab Book View: restore plain card view (sections must be open so cards show)
        document.body.classList.remove('lab-book-view');
        overview.removeAttribute('open');
        sections.forEach(d => d.setAttribute('open', ''));
        btn.classList.remove('active');
    }
}
