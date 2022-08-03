let country_select = document.getElementById("country");
let state_select = document.getElementById("state");

country_select.onchange = function () {
    country = country_select.value;
    if (country !== '- Select -') {
        fetch("/register/" + country).then(function (response) {
            response.json().then(function (data) {
                let newStatesHTML = '';

                for (let state of data.states) {
                    newStatesHTML += '<option value="' + state + '">' + state + '</option>';
                }

                state_select.innerHTML = newStatesHTML;
            });
        });
    } else {
        state_select.innerHTML = '<option value="- Select -">- Select -</option>'
    }
}