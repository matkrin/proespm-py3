/* const images = document.getElementsByClassName("stm_image"); */
const modal = document.getElementById("modal")
const modalImage = document.getElementById("modal-image")
const slideInfo = document.getElementById("slide-info");
const nextButton = document.getElementById("next");
const prevButton = document.getElementById("prev");
const closeButton = document.getElementById("close");

prevButton.addEventListener("click", () => plusSlides(-1))
nextButton.addEventListener("click", () => plusSlides(1))
closeButton.addEventListener("click", () => closeModal())


const imgs = document.getElementsByClassName("stm_image");
let slideIndex = 1;

let num_slides = 0;
for (let i = 0; i < imgs.length; ++i) {
    let img = imgs[i].firstElementChild
    img.addEventListener('click', () => {
        openModal();
        showSlides(parseInt(img.dataset.slideNum))
    })
    if (parseInt(img.dataset.slideNum) > num_slides) {
        num_slides = parseInt(img.dataset.slideNum);
    }
}

function showSlides(n) {
    slideIndex = n
    if (n > num_slides) {slideIndex = 1}
    if (n < 1) {slideIndex = num_slides}
    let newChilds = [];
    for (let i = 0; i < imgs.length; ++i) {
        let img = imgs[i].firstElementChild
        if (parseInt(img.dataset.slideNum) === slideIndex) { 
            let clone = img.cloneNode();
            clone.className = '';
            clone.classList.add("modal-image");
            newChilds.push(clone);
        }
    }
    console.log(newChilds);
    /* let newChild = slides[slideIndex-1] */
    /* newChild.classList.add("modal-image"); */
    modalImage.replaceChildren(...newChilds);
    slideInfo.innerText = newChilds[0].id
}

// Open the Modal
function openModal() {
  modal.style.display = "block";
  document.getElementById("top_button").style.display = 'none';
}

// Close the Modal
function closeModal() {
  modal.style.display = "none";
  document.getElementById("top_button").style.display = 'block';
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

