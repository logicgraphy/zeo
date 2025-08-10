import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

const LOCAL_STORAGE_KEY = 'fvai_consent_prefs_v1';

const defaultPreferences = {
  necessary: true,
  functional: false,
  analytics: false,
  marketing: false,
  doNotSell: false,
  consentGivenAt: null,
};

const ConsentContext = createContext({
  preferences: defaultPreferences,
  isBannerVisible: true,
  isPrivacyCenterOpen: false,
  acceptAll: () => {},
  rejectNonEssential: () => {},
  savePreferences: (_prefs) => {},
  openPrivacyCenter: () => {},
  closePrivacyCenter: () => {},
});

export function ConsentProvider({ children }) {
  const [preferences, setPreferences] = useState(defaultPreferences);
  const [isBannerVisible, setIsBannerVisible] = useState(true);
  const [isPrivacyCenterOpen, setIsPrivacyCenterOpen] = useState(false);

  // Load stored preferences on first mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Ensure necessary defaults
        const merged = { ...defaultPreferences, ...parsed };
        setPreferences(merged);
        setIsBannerVisible(false);
        syncDoNotSellCookie(merged?.doNotSell === true);
      } else {
        // Respect Global Privacy Control (GPC) and Do Not Track (DNT) by defaulting to opt-out
        const gpcEnabled = typeof navigator !== 'undefined' && navigator.globalPrivacyControl === true;
        const dntEnabled = typeof navigator !== 'undefined' && (navigator.doNotTrack === '1' || window.doNotTrack === '1');
        if (gpcEnabled || dntEnabled) {
          const minimal = {
            ...defaultPreferences,
            necessary: true,
            functional: false,
            analytics: false,
            marketing: false,
            doNotSell: true,
          };
          persistPreferences(minimal);
          setIsBannerVisible(false);
        } else {
          // Show banner when no stored consent
          setIsBannerVisible(true);
        }
      }
    } catch (e) {
      setIsBannerVisible(true);
    }
  }, []);

  const persistPreferences = (prefs) => {
    const enriched = {
      ...prefs,
      necessary: true,
      consentGivenAt: new Date().toISOString(),
    };
    setPreferences(enriched);
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(enriched));
    syncDoNotSellCookie(enriched.doNotSell === true);
  };

  const syncDoNotSellCookie = (optedOut) => {
    try {
      const value = optedOut ? '1' : '0';
      const expiry = new Date();
      expiry.setFullYear(expiry.getFullYear() + 1);
      document.cookie = `do_not_sell=${value}; path=/; SameSite=Lax; Secure; expires=${expiry.toUTCString()}`;
      // Optional: Set a simple usprivacy string for downstream tools (non-IAB compliant but indicative)
      // "1YNN" means user opted-out of sale; here we set "1YNN" when optedOut, otherwise "1---"
      const usp = optedOut ? '1YNN' : '1---';
      document.cookie = `usprivacy=${usp}; path=/; SameSite=Lax; Secure; expires=${expiry.toUTCString()}`;
    } catch (_) {
      // Best-effort only
    }
  };

  const acceptAll = () => {
    const all = {
      ...defaultPreferences,
      necessary: true,
      functional: true,
      analytics: true,
      marketing: true,
      doNotSell: false,
    };
    persistPreferences(all);
    setIsBannerVisible(false);
  };

  const rejectNonEssential = () => {
    const minimal = {
      ...defaultPreferences,
      necessary: true,
      functional: false,
      analytics: false,
      marketing: false,
      doNotSell: true,
    };
    persistPreferences(minimal);
    setIsBannerVisible(false);
  };

  const savePreferences = (newPrefs) => {
    persistPreferences({ ...defaultPreferences, ...newPrefs, necessary: true });
    setIsPrivacyCenterOpen(false);
    setIsBannerVisible(false);
  };

  const value = useMemo(
    () => ({
      preferences,
      isBannerVisible,
      isPrivacyCenterOpen,
      acceptAll,
      rejectNonEssential,
      savePreferences,
      openPrivacyCenter: () => setIsPrivacyCenterOpen(true),
      closePrivacyCenter: () => setIsPrivacyCenterOpen(false),
      setBannerVisible: setIsBannerVisible,
    }),
    [preferences, isBannerVisible, isPrivacyCenterOpen]
  );

  return <ConsentContext.Provider value={value}>{children}</ConsentContext.Provider>;
}

export function useConsent() {
  return useContext(ConsentContext);
}


