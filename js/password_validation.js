var myInput = document.getElementById("register_password");
var letter = document.getElementById("letter");
var letterMark = document.getElementById("letter-mark");
var capital = document.getElementById("capital");
var capitalMark = document.getElementById("capital-mark");
var number = document.getElementById("number");
var numberMark = document.getElementById("number-mark");
var length = document.getElementById("length");
var lengthMark = document.getElementById("length-mark");
const checkmark = "&#10003";
const errormark = "&#10007";

// When the user clicks on the password field, show the message box
myInput.onfocus = function() {
    document.getElementById("message").style.display = "block";
}

// When the user clicks outside of the password field, hide the message box
myInput.onblur = function() {
    document.getElementById("message").style.display = "none";
}

// When the user starts to type something inside the password field
myInput.onkeyup = function() {
  // Validate lowercase letters
  var lowerCaseLetters = /[a-z]/g;
  if(myInput.value.match(lowerCaseLetters)) {  
    letter.classList.remove("invalid");
    letter.classList.add("valid");
    letterMark.classList.remove("invalid");
    letterMark.classList.add("valid");
    letterMark.innerHTML = checkmark;
  } else {
    letter.classList.remove("valid");
    letter.classList.add("invalid");
    letterMark.classList.remove("valid");
    letterMark.classList.add("invalid");
    letterMark.innerHTML = errormark;

  }
  
  // Validate capital letters
  var upperCaseLetters = /[A-Z]/g;
  if(myInput.value.match(upperCaseLetters)) {  
    capital.classList.remove("invalid");
    capital.classList.add("valid");
    capitalMark.classList.remove("invalid");
    capitalMark.classList.add("valid");
    capitalMark.innerHTML = checkmark;
  } else {
    capital.classList.remove("valid");
    capital.classList.add("invalid");
    capitalMark.classList.remove("valid");
    capitalMark.classList.add("invalid");
    capitalMark.innerHTML = errormark;
  }

  // Validate numbers
  var numbers = /[0-9]/g;
  if(myInput.value.match(numbers)) {  
    number.classList.remove("invalid");
    number.classList.add("valid");
    numberMark.classList.remove("invalid");
    numberMark.classList.add("valid");
    numberMark.innerHTML = checkmark;
  } else {
    number.classList.remove("valid");
    number.classList.add("invalid");
    numberMark.classList.remove("valid");
    numberMark.classList.add("invalid");
    numberMark.innerHTML = errormark;
  }
  
  // Validate length
  if(myInput.value.length >= 8) {
    length.classList.remove("invalid");
    length.classList.add("valid");
    lengthMark.classList.remove("invalid");
    lengthMark.classList.add("valid");
    lengthMark.innerHTML = checkmark;
  } else {
    length.classList.remove("valid");
    length.classList.add("invalid");
    lengthMark.classList.remove("valid");
    lengthMark.classList.add("invalid");
    lengthMark.innerHTML = errormark;

  }
}