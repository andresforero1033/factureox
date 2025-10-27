(function () {
    const form = document.getElementById('contactForm');
    if (!form) return;
    const name = form.querySelector('#name');
    const email = form.querySelector('#email');
    const subject = form.querySelector('#subject');
    const message = form.querySelector('#message');

    function validate() {
        let ok = true;
        const checks = [
            { el: name, valid: !!name.value.trim() },
            { el: email, valid: email.validity.valid },
            { el: subject, valid: !!subject.value.trim() },
            { el: message, valid: message.value.trim().length >= 10 }
        ];
        checks.forEach(({ el, valid }) => el.classList.toggle('is-invalid', !valid));
        ok = checks.every(c => c.valid);
        return ok;
    }

    [name, email, subject, message].forEach(el => el && el.addEventListener('input', validate));

    form.addEventListener('submit', function (e) {
        if (!validate()) {
            e.preventDefault();
            e.stopPropagation();
        }
    });
})();
