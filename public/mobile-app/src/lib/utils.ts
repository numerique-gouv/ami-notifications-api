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

export const getTimestamp = (date: Date | null) => {
  if (date) {
    return Math.floor(date.getTime() / 1000);
  } else {
    return null;
  }
};

const getScrollableParent = (node: HTMLElement): HTMLElement | null => {
  let parent = node.parentElement;
  while (parent) {
    const { overflow, overflowY } = getComputedStyle(parent);
    const isScrollable =
      overflow === 'auto' ||
      overflow === 'scroll' ||
      overflowY === 'auto' ||
      overflowY === 'scroll';
    const hasOverflow = parent.scrollHeight > parent.clientHeight;
    if (isScrollable && hasOverflow) {
      return parent;
    }
    parent = parent.parentElement;
  }
  return null;
};

export const scrollToNode = (node: HTMLElement) => {
  const scrollableParent = getScrollableParent(node);
  if (!scrollableParent) {
    return;
  }
  const nodeTop = node.getBoundingClientRect().top;
  const parentTop = scrollableParent.getBoundingClientRect().top;
  const scrollTop = scrollableParent.scrollTop + nodeTop - parentTop - 5;
  scrollableParent.scrollTo({ top: scrollTop, behavior: 'smooth' });
};

export const scrollToInput = (event: FocusEvent & { currentTarget: HTMLElement }) => {
  const input = event.currentTarget || event.target;
  scrollToNode(input);
};

export const uniqueId = (): string => {
  return crypto.randomUUID();
};
