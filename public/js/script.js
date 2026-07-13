function setupTagSystem(inputId, listId, dataName) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && input.value.trim() !== "") {
            e.preventDefault();
            const val = input.value.trim();

            const li = document.createElement('li');
            li.innerHTML = `${val} <span class="remove-tag" style="cursor:pointer; margin-left:8px;">&times;</span>`;

            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = `${dataName}`; 
            hiddenInput.value = val;

            li.appendChild(hiddenInput);
            list.appendChild(li);

            input.value = "";

            li.querySelector('.remove-tag').onclick = () => {
                li.remove(); 
            };
        }
    });
}

setupTagSystem('Keyword_input', 'Keyword_list', 'keywords');
setupTagSystem('Director_input', 'Director_list', 'directors');
setupTagSystem('Cast_input', 'Cast_list', 'cast');


// userform
// let loginInp = document.querySelector("#login");
// let signupInp = document.querySelector("#signup");

// let loginForm = document.querySelector(".loginForm")
// let signupForm = document.querySelector(".signupForm")

// loginInp.addEventListener("checked" , (e) => {
//     signupForm.classList.add("hidden");  
//     if(loginForm.classList.contains(".hidden")) loginForm.classList.remove("hidden");
// })

// signupInp.addEventListener("checked" , (e) => {
//     loginForm.classList.add("hidden");
//     signupForm.classList.remove("hidden");
// })