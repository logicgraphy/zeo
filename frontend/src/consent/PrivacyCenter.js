import React, { useState, useEffect } from 'react';
import { useConsent } from './ConsentContext';

export default function PrivacyCenter() {
  const { preferences, isPrivacyCenterOpen, savePreferences, closePrivacyCenter } = useConsent();
  const [localPrefs, setLocalPrefs] = useState(preferences);

  useEffect(() => {
    if (isPrivacyCenterOpen) setLocalPrefs(preferences);
  }, [isPrivacyCenterOpen, preferences]);

  if (!isPrivacyCenterOpen) return null;

  const handleChange = (e) => {
    const { name, checked } = e.target;
    setLocalPrefs((p) => ({ ...p, [name]: checked }));
  };

  const handleSave = () => {
    savePreferences(localPrefs);
  };

  return (
    <div className="modal-overlay" onClick={closePrivacyCenter}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Privacy Preferences</h2>
          <button className="modal-close" onClick={closePrivacyCenter}>×</button>
        </div>
        <div className="modal-body">
          <h3>Cookie Categories</h3>
          <p>Control how we use cookies and similar technologies on your device.</p>

          <div className="prefs-list">
            <div className="prefs-item">
              <div className="prefs-row">
                <div>
                  <strong>Strictly Necessary</strong>
                  <p>Required for core site functionality. Always on.</p>
                </div>
                <div>
                  <input type="checkbox" checked readOnly />
                </div>
              </div>
            </div>

            <div className="prefs-item">
              <div className="prefs-row">
                <div>
                  <strong>Functional</strong>
                  <p>Remembers your preferences and improves usability.</p>
                </div>
                <div>
                  <input
                    type="checkbox"
                    name="functional"
                    checked={!!localPrefs.functional}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="prefs-item">
              <div className="prefs-row">
                <div>
                  <strong>Analytics</strong>
                  <p>Helps us understand site usage to improve performance.</p>
                </div>
                <div>
                  <input
                    type="checkbox"
                    name="analytics"
                    checked={!!localPrefs.analytics}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="prefs-item">
              <div className="prefs-row">
                <div>
                  <strong>Marketing</strong>
                  <p>Used to deliver relevant advertising and measure effectiveness.</p>
                </div>
                <div>
                  <input
                    type="checkbox"
                    name="marketing"
                    checked={!!localPrefs.marketing}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>
          </div>

          <h3>Do Not Sell or Share My Personal Information</h3>
          <p>We respect your right to opt out of the sale or sharing of personal information for targeted advertising.</p>
          <label className="dns-toggle">
            <input
              type="checkbox"
              name="doNotSell"
              checked={!!localPrefs.doNotSell}
              onChange={handleChange}
            />
            <span>Opt out of sale/sharing</span>
          </label>
        </div>
        <div className="modal-footer">
          <button className="cancel-button" onClick={closePrivacyCenter}>Cancel</button>
          <button className="submit-button" onClick={handleSave}>Save preferences</button>
        </div>
      </div>
    </div>
  );
}


