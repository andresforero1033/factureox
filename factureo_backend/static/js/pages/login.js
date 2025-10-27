(function () {
    const form = document.getElementById('loginForm');
    if (!form) return;
    const email = form.querySelector('#email');
    const password = form.querySelector('#password');

    function validate() {
        let ok = true;
        if (email) {
            const valid = email.value && email.validity.valid;
            email.classList.toggle('is-invalid', !valid);
            ok = ok && valid;
        }
        if (password) {
            const valid = password.value && password.value.length >= 6;
            password.classList.toggle('is-invalid', !valid);
            ok = ok && valid;
        }
        return ok;
    }

    email && email.addEventListener('input', validate);
    password && password.addEventListener('input', validate);
    form.addEventListener('submit', function (e) {
        if (!validate()) {
            e.preventDefault();
            e.stopPropagation();
        }
    });
})();
