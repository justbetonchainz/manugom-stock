document.querySelectorAll('[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

setTimeout(() => {
  document.querySelectorAll('.toast-stack .alert').forEach((element) => {
    bootstrap.Alert.getOrCreateInstance(element).close();
  });
}, 6500);

