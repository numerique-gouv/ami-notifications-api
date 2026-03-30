document.addEventListener('DOMContentLoaded', () => {
  const selects = document.querySelectorAll('#agent-forms select');
  const submitBtn = document.querySelector("button.fr-btn[type='submit']");

  if (submitBtn) {
    submitBtn.disabled = true;
  }

  const handleSelectChange = () => {
    const anyChanged = Array.from(selects).some((select) => select.value !== '');
    submitBtn.disabled = !anyChanged;
  };

  selects.forEach((select) => {
    select.addEventListener('change', handleSelectChange);
  });
});
