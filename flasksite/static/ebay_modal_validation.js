let ebayForm = document.getElementById('ebayForm')
let ebayModal = new bootstrap.Modal(document.getElementById('ebayModal'))

console.log("ebayModal:")
console.log(ebayModal)

let invalidCount = 1

ebayForm.addEventListener('submit', function (event) {
    let ebayFormData = new FormData(ebayForm)
    let csrf_token = document.getElementById("csrf_token").value

    ebayFormData.append("csrf_token", csrf_token)
    event.preventDefault()

    let validFlag = false;

    fetch("/profile/ebay/response", {
        method: "post",
        body: ebayFormData
    }).then(function (response) {
        response.json().then(function (data) {
            if (data.valid) {
                console.log('valid');
                validFlag = true;
            } else {
                for (let key of Object.keys(data)) {
                    console.log(key)
                    let invalidField = document.getElementById(key);
                    invalidField.classList.add("is-invalid");

                    let errorMessage = data[key][0]
                    let errorMessageHTML = "<span>" + errorMessage + "</span>"
                    let divHTML = "<div class='invalid-feedback'>" + errorMessageHTML + "</div>"

                    if (invalidCount === 1) {
                        invalidField.insertAdjacentHTML("afterend", divHTML)
                        invalidCount++
                    }
                }

                console.log('invalid');
                ebayModal.show();
                validFlag = false;
            }
            console.log(data);

            if (validFlag) {
                event.currentTarget.submit()
                window.location.reload(true);
            }
        })
    })
});