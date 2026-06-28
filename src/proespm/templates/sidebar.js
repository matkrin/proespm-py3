const menu = document.getElementById("menu");
const sidebar = document.getElementsByClassName("sidebar")[0];
let isSidebarOpen = false

/* Toggle the sidebar */
menu.addEventListener("click", () => {
    sidebar.style.width = isSidebarOpen ? "0%" : "25%"
    isSidebarOpen = !isSidebarOpen
})

const sidebarItems = document
    .getElementsByClassName("sidebar-content")[0]
    .getElementsByTagName("li");

/* Close sidebar on click; in Lab Book View open the target section first, then scroll */
for (it of sidebarItems) {
    const anchor = it.querySelector('a');
    if (!anchor) continue;

    anchor.addEventListener("click", (e) => {
        sidebar.style.width = "0%"
        isSidebarOpen = false

        if (document.body.classList.contains('lab-book-view')) {
            const href = anchor.getAttribute('href');
            if (href && href.startsWith('#')) {
                const target = document.getElementById(href.slice(1));
                const details = target?.querySelector(':scope > details');
                if (details && !details.hasAttribute('open')) {
                    e.preventDefault();                      // stop instant browser scroll
                    details.setAttribute('open', '');        // open section
                    history.pushState(null, null, href);     // update URL hash
                    requestAnimationFrame(() => {            // scroll after layout reflow
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    });
                }
            }
        }
    });
}
