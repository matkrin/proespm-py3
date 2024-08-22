const topButton = document.getElementById("top_button");

window.onscroll = () => scrollFunction();

/* When the user scrolls down 20px from the top of the document, show the button */
function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    topButton.style.display = "block";
  } else {
    topButton.style.display = "none";
  }
}

/* When the user clicks on the button, scroll to the top of the document */
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}
