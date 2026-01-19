function create_overview() {
    const stmImages = document.getElementsByClassName("stm_image_fw");
    const screenshotImgs = document.getElementsByClassName("screenshot-image");
    const images = [...stmImages, ...screenshotImgs];
    const overview = document.getElementById("overview");

    for (let i = 0; i < images.length; ++i) {
        let clone = images[i].firstElementChild.cloneNode();
        clone.classList = ''
        clone.style.width = "200px"
        clone.style.padding = "3px 3px 0 3px"
        let overviewEntry = document.createElement("div")
        overviewEntry.classList.add("overview-entry")
        let caption = document.createElement("p")
        let a = document.createElement('a')
        a.href = `#${clone.id}`
        a.appendChild(clone)
        caption.innerText = clone.id
        clone.id = ''
        overviewEntry.appendChild(a)
        overviewEntry.appendChild(caption)
        overview.appendChild(overviewEntry)
    }
}

create_overview()
