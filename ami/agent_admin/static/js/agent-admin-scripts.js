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
    const button = form.querySelector('button[type="submit"]');
    window.addEventListener('pageshow', (_ev) => {
      form.classList.remove('form-being-submitted');
      button.disabled = false;
    });

    form.addEventListener('submit', (_ev) => {
      if (form.classList.contains('form-being-submitted')) {
        _ev.preventDefault();
        return false;
      }
      form.classList.add('form-being-submitted');
      button.disabled = true;
    });
  }
});

const confirmModal = (id_modal) => {
  const modal = document.querySelector(`#${id_modal}`);
  if (modal && typeof window.dsfr === 'function') {
    window.dsfr(modal).modal.disclose();
  }
};

document.addEventListener('DOMContentLoaded', () => {
  const toasts = document.querySelectorAll('.toast-wrapper');
  const buttons = document.querySelectorAll('.toast-body-right-wrapper button');

  toasts.forEach((toast) => {
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 5000);
  });

  buttons.forEach((button) => {
    button.addEventListener('click', (_ev) => {
      if (!event.target) {
        return;
      }
      const element = event.target.parentNode.parentNode.parentNode.parentNode;
      element.parentNode.removeChild(element);
    });
  });
});
