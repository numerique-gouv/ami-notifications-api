export type Toast = {
  id: string;
  title: string;
  level: string;
};

class ToastStore {
  toasts: Toast[] = $state<Toast[]>([]);

  private uniqueId = (): string => {
    return Date.now().toString(36) + Math.random().toString(36).substring(2, 10);
  };

  addToast = (title: string, level: string) => {
    const id: string = this.uniqueId();
    const newToast: Toast = { id: id, title: title, level: level };
    this.toasts.push(newToast);
    setTimeout(() => this.removeToast(id), 3000);
  };

  removeToast = (id: string) => {
    this.toasts = this.toasts.filter((toast) => toast.id !== id);
  };
}

export const toastStore = new ToastStore();
