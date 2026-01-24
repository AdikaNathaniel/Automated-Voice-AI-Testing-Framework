import { useState, useCallback } from 'react';
import type { ModalType, ModalState } from '../components/Modal/Modal';

export const useModal = () => {
  const [modalState, setModalState] = useState<ModalState>({
    isOpen: false,
    type: 'info',
    message: '',
  });

  const showModal = useCallback(
    (
      message: string,
      options?: {
        type?: ModalType;
        title?: string;
        onConfirm?: () => void;
        confirmText?: string;
        cancelText?: string;
        showCancel?: boolean;
      }
    ) => {
      setModalState({
        isOpen: true,
        message,
        type: options?.type || 'info',
        title: options?.title,
        onConfirm: options?.onConfirm,
        confirmText: options?.confirmText,
        cancelText: options?.cancelText,
        showCancel: options?.showCancel,
      });
    },
    []
  );

  const showAlert = useCallback(
    (message: string, type: ModalType = 'info', title?: string) => {
      showModal(message, { type, title });
    },
    [showModal]
  );

  const showSuccess = useCallback(
    (message: string, title?: string) => {
      showModal(message, { type: 'success', title });
    },
    [showModal]
  );

  const showError = useCallback(
    (message: string, title?: string) => {
      showModal(message, { type: 'error', title });
    },
    [showModal]
  );

  const showWarning = useCallback(
    (message: string, title?: string) => {
      showModal(message, { type: 'warning', title });
    },
    [showModal]
  );

  const showConfirm = useCallback(
    (
      message: string,
      onConfirm: () => void,
      options?: {
        title?: string;
        confirmText?: string;
        cancelText?: string;
      }
    ) => {
      showModal(message, {
        type: 'confirm',
        onConfirm,
        showCancel: true,
        title: options?.title,
        confirmText: options?.confirmText || 'Confirm',
        cancelText: options?.cancelText || 'Cancel',
      });
    },
    [showModal]
  );

  const closeModal = useCallback(() => {
    setModalState((prev) => ({ ...prev, isOpen: false }));
  }, []);

  return {
    modalState,
    showModal,
    showAlert,
    showSuccess,
    showError,
    showWarning,
    showConfirm,
    closeModal,
  };
};

