// Open the Modal
function openModal() {
  document.getElementById("myModal").style.display = "block";
}

// Close the Modal
function closeModal() {
  document.getElementById("myModal").style.display = "none";
}

let slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  const slides = document.getElementsByClassName("mySlides");
  const captionText = document.getElementById("caption");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  slides[slideIndex-1].style.display = "block";
}


document.onkeydown = function(e) {
    e = e || window.event;
    switch(e.which || e.keyCode) {
        case 27: //ESC
        closeModal();
        break;

        case 20: // Caps-Lock
        closeModal();
        break;

        case 81: // q
        closeModal();
        break;

        case 38: // up-arrow
        plusSlides(-1);
        break;
        
        case 37: // left-arrow
        plusSlides(-1);
        break;
        
        case 72: // h
        plusSlides(-1);
        break;

        case 40: // down-arrow
        plusSlides(1);
        break;

        case 39: // right-arrow
        plusSlides(1);
        break;
        
        case 76: // l
        plusSlides(1);
        break;

        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
}
