export type ToastType = 'success' | 'info' | 'warning' | 'error';
export type DurationType = 3000 | 5000;

export class Toast {
  constructor(
    private _id: string,
    private _title: string,
    private _toastType: ToastType,
    private _duration: DurationType | null,
    private _hasCloseLink: boolean
  ) {}

  get id() {
    return this._id;
  }

  get title() {
    return this._title;
  }

  get toastType() {
    return this._toastType;
  }

  get duration() {
    return this._duration;
  }

  get hasCloseLink() {
    return this._hasCloseLink;
  }
}

class ToastStore {
  toasts: Toast[] = $state<Toast[]>([]);

  private uniqueId = (): string => {
    return Date.now().toString(36) + Math.random().toString(36).substring(2, 10);
  };

  private buildToast = (
    id: string,
    title: string,
    toastType: 'success' | 'info' | 'warning' | 'error',
    duration: 3000 | 5000 | null,
    hasCloseLink: boolean
  ) => {
    return new Toast(id, title, toastType, duration, hasCloseLink);
  };

  addToast = (
    title: string,
    toastType: ToastType,
    duration: DurationType | null,
    hasCloseLink: boolean
  ) => {
    const id: string = this.uniqueId();
    const newToast: Toast = this.buildToast(
      id,
      title,
      toastType,
      duration,
      hasCloseLink
    );
    this.toasts.push(newToast);
    if (duration) {
      setTimeout(() => this.removeToast(id), duration);
    }
  };

  removeToast = (id: string) => {
    this.toasts = this.toasts.filter((toast) => toast.id !== id);
  };
}

export const toastStore = new ToastStore();
