const images = document.getElementsByClassName("stm_image");
const modal = document.getElementById("modal")
const modalImage = document.getElementById("modal-image")
const slideInfo = document.getElementById("slide-info");
const nextButton = document.getElementById("next");
const prevButton = document.getElementById("prev");
const closeButton = document.getElementById("close");

prevButton.addEventListener("click", () => plusSlides(-1))
nextButton.addEventListener("click", () => plusSlides(1))
closeButton.addEventListener("click", () => closeModal())

const imgs = []
for (let i of images) {
    imgs.push(i.firstElementChild)
}
const slides = imgs.map(i => {
    const clone = i.cloneNode()
    clone.className = '';
    return clone
})
let slideIndex = 1;

/* console.log(imgs) */
imgs.forEach(i => {
    i.addEventListener('click', () => {
        openModal();
        showSlides(parseInt(i.dataset.slideNum));
    })
})



// Open the Modal
function openModal() {
  modal.style.display = "block";
}

// Close the Modal
function closeModal() {
  modal.style.display = "none";
}

/* showSlides(slideIndex); */

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}


function showSlides(n) {
    slideIndex = n
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    let newChild = slides[slideIndex-1]
    newChild.classList.add("modal-image");
    modalImage.replaceChildren(newChild);
    slideInfo.innerText = slides[slideIndex-1].id
}


document.onkeydown = function(e) {
    e = e || window.event;
    switch(e.which || e.keyCode) {
        case 27: //ESC
        case 81: // q
        case 20: // Caps-Lock
        closeModal();
        break;

        case 37: // left-arrow
        case 38: // up-arrow
        case 72: // h
        plusSlides(-1);
        break;
        
        case 39: // right-arrow
        case 40: // down-arrow
        case 76: // l
        plusSlides(1);
        break;

        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
}

