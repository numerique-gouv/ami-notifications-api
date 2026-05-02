import { render, screen } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import Modal from './Modal.svelte';

const { mockMount, mockUnmount, mockDisclose, mockConceal, mockDsfr } = vi.hoisted(
  () => {
    const mockDisclose = vi.fn();
    const mockConceal = vi.fn();
    const mockDsfr = vi.fn(() => ({
      modal: { disclose: mockDisclose, conceal: mockConceal },
    }));
    const mockMount = vi.fn(
      (
        _component: unknown,
        _attrs: { target: HTMLElement; props: Record<string, unknown> }
      ) => ({ destroy: vi.fn() })
    );
    const mockUnmount = vi.fn();

    return { mockMount, mockUnmount, mockDisclose, mockConceal, mockDsfr };
  }
);

vi.mock('svelte', async (importOriginal) => {
  const actual = await importOriginal<typeof import('svelte')>();
  return {
    ...actual,
    mount: mockMount,
    unmount: mockUnmount,
  };
});

const FakeComponent = vi.fn();

describe('Modal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.dsfr = mockDsfr;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test('should render modal with correct id and title', () => {
    // Given
    render(Modal, {
      props: {
        id: 'test-modal',
        title: 'Title',
        component: FakeComponent,
      },
    });

    // When
    const dialog = screen.getByRole('dialog', { hidden: true });

    // Then
    expect(dialog).toBeInTheDocument();
    expect(dialog).toHaveAttribute('id', 'test-modal');
    expect(dialog).toHaveAttribute('aria-labelledby', 'test-modal-title');
    expect(screen.getByText('Title')).toBeInTheDocument();
  });

  test('Should open component with props', async () => {
    // Given
    const customProps = { foo: 'bar' };
    const { component } = render(Modal, {
      props: {
        id: 'test-modal',
        title: 'Title',
        component: FakeComponent,
        props: customProps,
      },
    });

    // When
    await component.open();

    // Then
    expect(mockMount).toHaveBeenCalledOnce();
    const [mountedComponent, mountOptions] = mockMount.mock.calls[0];
    expect(mountedComponent).toBe(FakeComponent);
    expect(mountOptions.props).toMatchObject({
      foo: 'bar',
      onClose: expect.any(Function),
      footerTarget: expect.any(HTMLElement),
    });
  });

  test('open should call dsfr.modal.disclose', async () => {
    // Given
    const { component } = render(Modal, {
      props: { id: 'test-modal', title: 'Title', component: FakeComponent },
    });

    // When
    await component.open();

    // Then
    expect(mockDsfr).toHaveBeenCalled();
    expect(mockDisclose).toHaveBeenCalledOnce();
  });

  test('onClose should call dsfr.modal.conceal', async () => {
    // Given
    const { component } = render(Modal, {
      props: { id: 'test-modal', title: 'Title', component: FakeComponent },
    });
    await component.open();

    // When
    const mountOptions = mockMount.mock.calls[0][1] as unknown as {
      props: { onClose: () => void };
    };
    mountOptions.props.onClose();

    // Then
    expect(mockConceal).toHaveBeenCalledOnce();
  });

  test('dsfr.modal.conceal whould call onCloseCustom', async () => {
    // Given
    const { component } = render(Modal, {
      props: { id: 'test-modal', title: 'Title', component: FakeComponent },
    });
    await component.open();

    // When
    const mountOptions = mockMount.mock.calls[0][1] as unknown as {
      props: { onClose: () => void };
    };
    mountOptions.props.onClose();

    // Then
    expect(mockConceal).toHaveBeenCalledOnce();
  });

  test('dsfr.conceal listner should be removed when modal is unmounted', async () => {
    // Given
    const removeEventListenerSpy = vi.spyOn(
      HTMLDialogElement.prototype,
      'removeEventListener'
    );
    const { unmount: unmountComponent } = render(Modal, {
      props: { id: 'test-modal', title: 'Title', component: FakeComponent },
    });

    // When
    unmountComponent();

    // Then
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'dsfr.conceal',
      expect.any(Function)
    );
  });
});
