export const ariaHideDecorativeEmoji = (
  st: string,
  escapeHtml: boolean = true
): string => {
  // escape HTML then apply markup to emojis
  let result = st;
  if (escapeHtml) {
    result = result
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');
  }
  return result.replaceAll(/([^0-9\P{Emoji}])/gu, '<span aria-hidden="true">$1</span>');
};
