export const formatDate = (data: string | Date) => {
  let date: Date;
  if (typeof data === 'string') {
    date = new Date(data);
  } else {
    date = data;
  }
  const options: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  };
  return date.toLocaleDateString('fr-FR', options);
};

export const dateToISO = (date: Date | null) => {
  if (date === null) {
    return '';
  }
  // Return date in ISO format, with user timezone
  const year = date.getFullYear();
  const monthOptions: Intl.DateTimeFormatOptions = {
    month: '2-digit',
  };
  const month = date.toLocaleDateString('fr-FR', monthOptions);
  const dayOptions: Intl.DateTimeFormatOptions = {
    day: '2-digit',
  };
  const day = date.toLocaleDateString('fr-FR', dayOptions);
  return `${year}-${month}-${day}`;
};

export const scrollToNode = (node: HTMLElement) => {
  const nav = document.querySelector('nav');
  if (!nav) {
    return;
  }
  const nodeOffsetTop =
    node.getBoundingClientRect().top -
    nav.getBoundingClientRect().bottom +
    (document.scrollingElement?.scrollTop || 0) -
    5; // Just a small margin to avoid cutting the top of the node
  window.scrollTo({ top: nodeOffsetTop, behavior: 'smooth' });
};

export const scrollToInput = (event: FocusEvent & { currentTarget: HTMLElement }) => {
  const input = event.currentTarget || event.target;
  scrollToNode(input);
};
