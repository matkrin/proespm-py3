function toggleExpand(){
document.body.querySelectorAll('details')
    .forEach((e) => {
        (e.hasAttribute('open') && e.id != "overview_root" && !e.classList.contains("elab-entry"))
            ? e.removeAttribute('open')
            : e.setAttribute('open',false);
    })
}
