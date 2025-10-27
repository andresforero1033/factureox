(function(){
  const form = document.getElementById('registerForm');
  if(!form) return;
  const name = form.querySelector('#name');
  const email = form.querySelector('#email');
  const username = form.querySelector('#username');
  const password = form.querySelector('#password');

  function validate(){
    let ok = true;
    if(name){
      const valid = !!name.value.trim();
      name.classList.toggle('is-invalid', !valid);
      ok = ok && valid;
    }
    if(email){
      const valid = email.value && email.validity.valid;
      email.classList.toggle('is-invalid', !valid);
      ok = ok && valid;
    }
    if(username){
      const valid = username.value && username.value.length >= 3;
      username.classList.toggle('is-invalid', !valid);
      ok = ok && valid;
    }
    if(password){
      const valid = password.value && password.value.length >= 6;
      password.classList.toggle('is-invalid', !valid);
      ok = ok && valid;
    }
    return ok;
  }

  [name,email,username,password].forEach(el => el && el.addEventListener('input', validate));
  form.addEventListener('submit', function(e){
    if(!validate()){
      e.preventDefault();
      e.stopPropagation();
    }
  });
})();
