export const ariaHideDecorativeEmoji = (
  st: string | undefined,
  escapeHtml: boolean = true
): string => {
  // escape HTML then apply markup to emojis
  if (st === undefined) {
    return '';
  }
  let result = st;
  if (escapeHtml) {
    result = result
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');
  }
  return result.replaceAll(/([^0-9\P{Emoji}])/gu, '<span aria-hidden="true">$1</span>');
};

export const removeDecorativeEmoji = (
  st: string | undefined,
  escapeHtml: boolean = true
): string => {
  // escape HTML then remove emojis
  if (st === undefined) {
    return '';
  }
  let result = st;
  if (escapeHtml) {
    result = result
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');
  }
  return result.replaceAll(/([^0-9\P{Emoji}])/gu, '');
};
