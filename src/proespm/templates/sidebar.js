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

/* Close the sidebar when one element is clicked */
for (it of sidebarItems) {
    it.addEventListener("click", () => {
        sidebar.style.width = "0%"
        isSidebarOpen = false
    })
}
