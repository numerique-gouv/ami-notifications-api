document.addEventListener('DOMContentLoaded', () => {
  const selects = document.querySelectorAll('#agent-forms select');
  const submitBtn = document.querySelector("#agent-forms button.fr-btn[type='submit']");

  if (submitBtn) {
    submitBtn.disabled = true;
  }

  const initSelectChange = (select) => {
    select.dataset.initial = select.value;
  };
  const handleSelectChange = () => {
    const anyChanged = Array.from(selects).some(
      (select) => select.value !== select.dataset.initial
    );
    submitBtn.disabled = !anyChanged;
  };

  selects.forEach((select) => {
    initSelectChange(select);
    select.addEventListener('change', handleSelectChange);
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.form-disable-on-submit');

  if (form) {
    form.addEventListener('submit', (_ev) => {
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
    });
  }
});
