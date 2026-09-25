import { render } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import Toggle from './Toggle.svelte';

describe('/Toggle.svelte', () => {
  test('should mark emojis in tags', async () => {
    // Given
    const toggle = {
      id: 'test',
      label: 'label',
      isChecked: false,
      onChangeAction: vi.fn(),
      onRemoveAction: vi.fn(),
      tags: [{ id: 'tag', label: '<script>Tag</script> 🏠', removable: false }],
    };

    // When
    render(Toggle, { props: toggle });

    // Then
    expect(document.querySelector('script')).not.toBeInTheDocument();
    expect(document.querySelector('[aria-hidden]')).toBeInTheDocument();
  });
});
