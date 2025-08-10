import React from 'react';
import { useConsent } from './ConsentContext';

export default function CookieBanner() {
  const { isBannerVisible, acceptAll, rejectNonEssential, openPrivacyCenter } = useConsent();

  if (!isBannerVisible) return null;

  return (
    <div className="cookie-banner">
      <div className="cookie-banner__content">
        <div className="cookie-banner__text">
          We use cookies to enhance your experience, analyze usage, and improve our services. You can accept all, reject non-essential, or manage preferences. We also honor a "Do Not Sell My Personal Information" opt-out.
        </div>
        <div className="cookie-banner__actions">
          <button className="cookie-btn secondary" onClick={rejectNonEssential}>Reject non-essential</button>
          <button className="cookie-btn tertiary" onClick={openPrivacyCenter}>Manage preferences</button>
          <button className="cookie-btn primary" onClick={acceptAll}>Accept all</button>
        </div>
      </div>
    </div>
  );
}


