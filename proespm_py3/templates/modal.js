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

/* const imgs = [] */
/* for (let i of images) { */
/*     imgs.push(i.firstElementChild) */
/* } */

let slideIndex = 1;

const imgs = document.getElementsByTagName("img")
console.log(imgs);

let num_slides = 0;
for (let i = 0; i < imgs.length; ++i) {
    imgs[i].addEventListener('click', () => {
        openModal();
        showSlides(parseInt(imgs[i].dataset.slideNum))
    })
    if (parseInt(imgs[i].dataset.slideNum) > num_slides) {
        num_slides = parseInt(imgs[i].dataset.slideNum);
    }
}
console.log(num_slides)

/* const slides = imgs.map(i => { */
/*     const clone = i.cloneNode() */
/*     clone.className = ''; */
/*     return clone */
/* }) */
/* console.log(images) */
/* console.log(slides) */

/* console.log(imgs) */
/* imgs.forEach(i => { */
/*     i.addEventListener('click', () => { */
/*         openModal(); */
/*         showSlides(parseInt(i.dataset.slideNum)); */
/*     }) */
/* }) */


function showSlides(n) {
    slideIndex = n
    if (n > num_slides) {slideIndex = 1}
    if (n < 1) {slideIndex = num_slides}
    let newChilds = [];
    for (let i = 0; i < imgs.length; ++i) {
        if (parseInt(imgs[i].dataset.slideNum) === slideIndex) { 
            let clone = imgs[i].cloneNode();
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

