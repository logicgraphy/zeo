import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { ConsentProvider } from './consent/ConsentContext';
import CookieBanner from './consent/CookieBanner';
import PrivacyCenter from './consent/PrivacyCenter';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ConsentProvider>
      <App />
      <CookieBanner />
      <PrivacyCenter />
    </ConsentProvider>
  </React.StrictMode>
); 