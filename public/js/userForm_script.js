let loginInp = document.querySelector("#login")
let signupInp = document.querySelector("#signup")

let loginForm = document.querySelector(".loginForm");
let signupForm = document.querySelector(".signupForm");

loginInp.addEventListener("change" , (e) => {
    if(loginInp.checked) {
        signupForm.classList.add("hidden")
        loginForm.classList.remove("hidden")
    }
});

signupInp.addEventListener("change" , (e) => {
    if(signupInp.checked) {
        loginForm.classList.add("hidden")
        signupForm.classList.remove("hidden")
    }
});