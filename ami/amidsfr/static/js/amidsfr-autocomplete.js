document.addEventListener('DOMContentLoaded', () => {
  const matches = document.querySelectorAll('.amidsfr-autocomplete input');
  const buttonMatches = document.querySelectorAll('.amidsfr-autocomplete button');
  matches.forEach((input) => {
    ['input', 'focus'].forEach((event) => {
      input.addEventListener(event, (_ev) => {
        autocompleteHandler(_ev);
      });
    });
    input.addEventListener('focusout', (_ev) => {
      removeAutocompleteHandler(_ev);
    });
  });
  buttonMatches.forEach((button) => {
    button.addEventListener('click', (_ev) => {
      submitHandler(_ev);
    });
  });
});

const autocompleteHandler = (event) => {
  if (!event.target) {
    return;
  }
  debounce(event.target);
};

const removeAutocompleteHandler = (event) => {
  if (!event.target) {
    return;
  }
  removeResults(event.target);
};

const submitHandler = (event) => {
  if (!event.target) {
    return;
  }
  event.target.form.submit();
};

let timer;
const debounce = (element) => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    filterValues(element);
  }, 750);
};

const filterValues = async (element) => {
  const url = element.dataset.autocompleteUrl;
  filteredValues = [];
  if (element.value) {
    try {
      const response = await callEndpoint(url, element.value);
      if (!response.results) {
        return;
      }
      filteredValues = response.results;
    } catch (error) {
      console.error(error);
    }
  }
  displayResults(element, filteredValues);
};

const callEndpoint = async (url, value) => {
  const encodedValue = encodeURI(value);
  const endpoint_headers = {
    accept: 'application/json',
  };
  const response = await fetch(`${url}?q=${encodedValue}`, {
    headers: endpoint_headers,
  });

  if (response.status >= 400) {
    return { errorCode: 'endpoint-unavailable', errorMessage: 'Endpoint unavailable' };
  }
  let result = {};

  try {
    result = await response.json();
  } catch (error) {
    console.error(error);
  }

  return {
    results: result.data,
  };
};

const removeResults = (element) => {
  const id = `${element.id}-autocomplete-results`;
  const autocompleteDiv = document.querySelector(`#${id}`);
  if (autocompleteDiv !== null) {
    // remove element if exists
    autocompleteDiv.remove();
  }
};

const displayResults = (element, results) => {
  const id = `${element.id}-autocomplete-results`;
  removeResults(element);
  autocompleteDiv = document.createElement('div');
  autocompleteDiv.id = id;
  autocompleteDiv.className = 'amidsfr-autocomplete-results';
  const autocompleteUl = document.createElement('ul');
  autocompleteUl.className = 'amidsfr-autocomplete-results-list';
  autocompleteDiv.appendChild(autocompleteUl);

  if (results.length) {
    element.parentNode.insertBefore(autocompleteDiv, element.nextSibling);
  }
  results.forEach((result) => {
    const li = document.createElement('li');
    li.className = 'amidsfr-autocomplete-results-item';
    const button = document.createElement('button');
    button.innerHTML = `<p>${result.value}</p>`;
    li.appendChild(button);
    autocompleteUl.appendChild(li);
    button.addEventListener('mousedown', (_ev) => {
      _ev.preventDefault();
      element.value = _ev.target.textContent;
      autocompleteDiv.remove();
      const button = element.form.querySelector('.amidsfr-autocomplete button');
      if (button) {
        button.click();
      }
    });
  });
};
