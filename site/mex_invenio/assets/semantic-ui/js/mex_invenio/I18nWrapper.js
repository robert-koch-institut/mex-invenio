import React, { Suspense, useEffect, useState } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';

const I18nWrapper = ({ children }) => {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (window.i18nReady) {
      setReady(true);
      return;
    }
    const check = () => {
      if (window.i18nReady || i18n.isInitialized) {
        setReady(true);
      }
    };
    const id = setInterval(check, 50);
    return () => clearInterval(id);
  }, []);

  if (!ready) return <div>Loading i18n...</div>;

  return (
    <I18nextProvider i18n={i18n}>
      <Suspense fallback="Loading...">{children}</Suspense>
    </I18nextProvider>
  );
};

export default I18nWrapper;
