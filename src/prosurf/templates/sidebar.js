const menu = document.getElementById("menu");
const sidebar = document.getElementsByClassName("sidebar")[0];
let isSidebarOpen = false

menu.addEventListener("click", () => {
    sidebar.style.width = isSidebarOpen ? "0%" : "25%"
    isSidebarOpen = !isSidebarOpen
})
