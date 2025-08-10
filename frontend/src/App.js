import React, { useState } from 'react';
import './App.css';
import { useConsent } from './consent/ConsentContext';

const API_BASE_URL = 'http://localhost:8000';

// Header Component
const Header = ({ onLogoClick }) => {
  return (
    <header className="app-header-nav">
      <div className="header-content">
        <div className="logo" onClick={onLogoClick}>
          <span className="logo-icon">🚀</span>
          <span className="logo-text">Force Vector AI</span>
        </div>
      </div>
    </header>
  );
};

// Terms & Conditions Modal Component
const TermsModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Terms & Conditions</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <h3>1. Acceptance of Terms</h3>
          <p>By accessing and using Force Vector AI's analysis service, you accept and agree to be bound by the terms and provision of this agreement.</p>
          
          <h3>2. Service Description</h3>
          <p>Force Vector AI provides automated analysis and recommendations for websites. Our service includes website analysis, grade scoring, and actionable improvement suggestions.</p>
          
          <h3>3. Privacy Policy</h3>
          <p>We collect and process website URLs and email addresses solely for the purpose of providing our analysis service. We do not share your information with third parties without your consent.</p>
          
          <h3>4. Limitation of Liability</h3>
          <p>Force Vector AI provides analysis on an "as is" basis. We make no warranties about the accuracy, reliability, completeness, or timeliness of our analysis results.</p>
          
          <h3>5. User Responsibilities</h3>
          <p>Users are responsible for providing accurate website URLs and maintaining the confidentiality of any account information.</p>
          
          <h3>6. Modifications</h3>
          <p>We reserve the right to modify these terms at any time. Continued use of the service constitutes acceptance of modified terms.</p>
          
          <h3>7. Contact Information</h3>
          <p>For questions about these terms, please contact us at support@forcevector.ai</p>
        </div>
        <div className="modal-footer">
          <button className="modal-button" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

// Contact Us Modal Component
const ContactModal = ({ isOpen, onClose }) => {
  const { preferences } = useConsent();
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [captchaChecked, setCaptchaChecked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  if (!isOpen) return null;

  const updateField = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!captchaChecked) {
      setError('Please complete the captcha before submitting.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Consent-Do-Not-Sell': preferences?.doNotSell ? '1' : '0',
          'X-Consent-Functional': preferences?.functional ? '1' : '0',
          'X-Consent-Analytics': preferences?.analytics ? '1' : '0',
          'X-Consent-Marketing': preferences?.marketing ? '1' : '0',
          'Sec-GPC': (typeof navigator !== 'undefined' && navigator.globalPrivacyControl) ? '1' : '0',
        },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || 'Failed to submit contact form');
      setSuccess(data?.message || 'Thanks! We will reach out soon.');
      setForm({ name: '', email: '', subject: '', message: '' });
      setCaptchaChecked(false);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Contact Us</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="cu-name">Name *</label>
                <input id="cu-name" name="name" type="text" value={form.name} onChange={updateField} required placeholder="Your full name" />
              </div>
              <div className="form-group">
                <label htmlFor="cu-email">Email *</label>
                <input id="cu-email" name="email" type="email" value={form.email} onChange={updateField} required placeholder="you@example.com" />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="cu-subject">Subject</label>
              <input id="cu-subject" name="subject" type="text" value={form.subject} onChange={updateField} placeholder="How can we help?" />
            </div>
            <div className="form-group">
              <label htmlFor="cu-message">Message *</label>
              <textarea id="cu-message" name="message" rows="4" value={form.message} onChange={updateField} required placeholder="Tell us a bit about your needs..." />
            </div>

            <div className="captcha-box">
              <label className="captcha-label">
                <input type="checkbox" checked={captchaChecked} onChange={(e) => setCaptchaChecked(e.target.checked)} />
                <span>I’m not a robot</span>
              </label>
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <div className="button-group">
              <button type="submit" className="submit-button" disabled={loading || !form.name || !form.email || !form.message || !captchaChecked}>
                {loading ? 'Sending...' : 'Send Message'}
              </button>
              <button type="button" className="cancel-button" onClick={onClose}>Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Footer Component
const Footer = () => {
  const { openPrivacyCenter } = useConsent();
  const [showTerms, setShowTerms] = useState(false);
  const [showContact, setShowContact] = useState(false);

  return (
    <>
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-links">
            <button 
              className="footer-link" 
              onClick={() => setShowTerms(true)}
            >
              Terms of Service
            </button>
            <span className="footer-separator">|</span>
            <button
              className="footer-link"
              onClick={openPrivacyCenter}
            >
              Privacy & Cookie Settings
            </button>
            <span className="footer-separator">|</span>
            <button
              className="footer-link"
              onClick={() => setShowContact(true)}
            >
              Contact Us
            </button>
            <span className="footer-separator">|</span>
            <span className="footer-text">© 2025 Force Vector AI. All rights reserved.</span>
          </div>
        </div>
      </footer>
      <TermsModal 
        isOpen={showTerms} 
        onClose={() => setShowTerms(false)} 
      />
      <ContactModal 
        isOpen={showContact}
        onClose={() => setShowContact(false)}
      />
    </>
  );
};

// URL Input Component (Step 1)
const UrlInputForm = ({ onAnalyze, loading, error }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAnalyze(url.trim());
    }
  };

  const isValidUrl = (string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  return (
    <div className="form-container">
      <h2>Optimize your website for AI</h2>
      <p className="subtitle">Enter your website URL to get a quick analysis</p>
      
      <form onSubmit={handleSubmit} className="url-form">
        <div className="form-group">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            required
            className="url-input"
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        {loading && (
          <div className="wait-indicator" aria-live="polite" aria-busy="true">
            <img src="/img/wait.png" alt="Loading" className="wait-icon wait-icon--large" />
          </div>
        )}

        <button 
          type="submit" 
          className="analyze-button" 
          disabled={loading || !url.trim() || !isValidUrl(url)}
        >
          {loading ? 'Analyzing...' : 'Analyze Website'}
        </button>
      </form>
      
      <p className="help-text">
        Assess your website's readiness for AI-driven discovery and search
      </p>
    </div>
  );
};

// Quick Score Result Component (Step 2)
const QuickGradeResult = ({ score, url, categories, onRequestReport, loading, error }) => {
  const [email, setEmail] = useState('');
  const [showEmailForm, setShowEmailForm] = useState(false);

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    if (email.trim()) {
      onRequestReport(email.trim());
    }
  };

  const getGradeColor = (value) => {
    if (value >= 90) return '#4CAF50';
    if (value >= 70) return '#FF9800';  
    if (value >= 50) return '#FF5722';
    return '#F44336';
  };

  const getGradeLetter = (grade) => {
    if (grade >= 90) return 'A';
    if (grade >= 80) return 'B';
    if (grade >= 70) return 'C';
    if (grade >= 60) return 'D';
    return 'F';
  };

  const cat = categories || {};

  const getCatColor = (v) => {
    if (v >= 5) return '#4CAF50';
    if (v >= 4) return '#8BC34A';
    if (v >= 3) return '#FFB300';
    if (v >= 2) return '#FF7043';
    return '#F44336';
  };

  return (
    <div className="form-container">
      <h2>Your AI readiness Grade</h2>
      {url && (
        <p className="grade-url"><a href={url} target="_blank" rel="noreferrer">{url}</a></p>
      )}
      
      <div className="grade-display">
        <div className="grade-circle" style={{ borderColor: getGradeColor(score) }}>
          <span className="grade-letter" style={{ color: getGradeColor(score) }}>
            {getGradeLetter(score)}
          </span>
          <span className="grade-number">{score}/100</span>
        </div>
      </div>
      
      <div className="category-grid">
        <div className="category-card">
          <div className="category-header">
            <span>Content Quality</span>
            <span className="category-score" style={{ color: getCatColor(cat?.content_quality?.score) }}>
              {cat?.content_quality?.score ?? '-'}&#8239;/&#8239;5
            </span>
          </div>
          <p className="category-reason">{cat?.content_quality?.reason || '—'}</p>
        </div>
        <div className="category-card">
          <div className="category-header">
            <span>Structure Optimization</span>
            <span className="category-score" style={{ color: getCatColor(cat?.structure_optimization?.score) }}>
              {cat?.structure_optimization?.score ?? '-'}&#8239;/&#8239;5
            </span>
          </div>
          <p className="category-reason">{cat?.structure_optimization?.reason || '—'}</p>
        </div>
        <div className="category-card">
          <div className="category-header">
            <span>Authority & Trust</span>
            <span className="category-score" style={{ color: getCatColor(cat?.authority_trust?.score) }}>
              {cat?.authority_trust?.score ?? '-'}&#8239;/&#8239;5
            </span>
          </div>
          <p className="category-reason">{cat?.authority_trust?.reason || '—'}</p>
        </div>
      </div>

      {!showEmailForm ? (
        <div className="email-prompt">
          <h3>Want a detailed report?</h3>
          <p>Enter your email to receive your comprehensive AI readiness analysis</p>
          <button 
            className="email-prompt-button"
            onClick={() => setShowEmailForm(true)}
          >
            Get Detailed Report
          </button>
        </div>
      ) : (
        <form onSubmit={handleEmailSubmit} className="email-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          <div className="button-group">
            <button 
              type="submit" 
              className="submit-button" 
              disabled={loading || !email.trim()}
            >
              {loading ? 'Sending...' : 'Send Report'}
            </button>
            
            <button 
              type="button" 
              className="cancel-button"
              onClick={() => setShowEmailForm(false)}
            >
              Cancel
            </button>
          </div>          
        </form>
      )}
    </div>
  );
};

// Email Verification Component (Step 4)
const EmailVerificationForm = ({ email, onVerify, onResend, loading, error, success }) => {
  const [code, setCode] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (code.trim().length === 6) {
      onVerify(code.trim());
    }
  };

  return (
    <div className="form-container">
      <h2>Verify Your Email</h2>
      <p className="verification-message">
        We've sent a 6-digit verification code to <strong>{email}</strong>
      </p>
      
      <form onSubmit={handleSubmit} className="verification-form">
        <div className="form-group">
          <label htmlFor="code">Verification Code</label>
          <input
            type="text"
            id="code"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="123456"
            maxLength="6"
            className="code-input"
            required
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        <div className="button-group">
          <button 
            type="submit" 
            className="submit-button" 
            disabled={loading || code.length !== 6}
          >
            {loading ? 'Verifying...' : 'Verify Email'}
          </button>
          
          <button 
            type="button" 
            className="resend-button" 
            onClick={onResend} 
            disabled={loading}
          >
            Resend Code
          </button> 
        </div>        
      </form>
      
      {loading && success && (
        <div className="loading-spinner" style={{ marginTop: '16px' }}>
          <div className="spinner"></div>
          <p>{success}</p>
        </div>
      )}

      <p className="help-text">Check your console for the verification code (demo mode)</p>
    </div>
  );
};

// Detailed Report Component
const DetailedReport = ({ reportData, onChooseDIY, onChooseHire, loading }) => {
  if (loading) {
    return (
      <div className="form-container">
        <h2>Generating Your Report</h2>
        <div className="wait-indicator" aria-live="polite" aria-busy="true">
          <img src="/img/wait.png" alt="Loading" className="wait-icon wait-icon--large" />
        </div>
        <p style={{ marginTop: '12px' }}>Analyzing your website in detail...</p>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="form-container">
        <h2>Report Not Available</h2>
        <p>Unable to generate detailed report. Please try again.</p>
      </div>
    );
  }

  const meta = reportData.meta || {};
  const exec = reportData.executive_summary || {};
  const overall = reportData.overall_findings || {};
  const strengths = reportData.strengths || {};
  const weaknesses = reportData.weaknesses || {};
  const implications = reportData.implications_for_aeo || {};
  const recommendations = reportData.recommendations || [];
  const checklist = reportData.quick_win_checklist || [];
  const pageScores = reportData.page_scores || [];
  const abTests = reportData.ab_testing_plan || [];
  const kpis = reportData.kpis_to_monitor || [];

  return (
    <div className="form-container report-container">
      <h2>{meta.report_title || 'AEO Site Report'}</h2>
      
      <div className="report-summary">
        <div className="score-display">
          <h3>Overall Score: {meta.overall_score ?? '-'} / 100</h3>
        </div>
        <p><strong>Scope:</strong> {meta.scope || '—'}</p>
        <p><strong>Analyzed At:</strong> {meta.analyzed_at || '—'}</p>
      </div>

      <section className="issues-summary">
        <h3>Executive Summary</h3>
        <p>{exec.summary_paragraph}</p>
        {Array.isArray(exec.highlights) && exec.highlights.length > 0 && (
          <ul className="issues-list">
            {exec.highlights.map((h, i) => (
              <li key={i} className="issue"><span className="issue-text">{h}</span></li>
            ))}
          </ul>
        )}
      </section>

      <section className="issues-summary">
        <h3>Overall Findings</h3>
        <ul className="issues-list">
          <li className="issue"><span className="issue-text">Content Quality: {overall.content_quality?.score ?? '-'} / 5 — {overall.content_quality?.notes || ''}</span></li>
          <li className="issue"><span className="issue-text">Structure: {overall.structure?.score ?? '-'} / 5 — {overall.structure?.notes || ''}</span></li>
          <li className="issue"><span className="issue-text">Authority Signals: {overall.authority_signals?.score ?? '-'} / 5 — {overall.authority_signals?.notes || ''}</span></li>
        </ul>
        {overall.impact && <p><strong>Impact:</strong> {overall.impact}</p>}
        {Array.isArray(overall.common_themes) && overall.common_themes.length > 0 && (
          <>
            <h4>Common Themes</h4>
            <ul className="issues-list">
              {overall.common_themes.map((t, i) => (
                <li key={i} className="issue"><span className="issue-text">{t}</span></li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className="issues-summary">
        <h3>Strengths</h3>
        <div className="two-col">
          <div>
            <h4>Brand & Domain Trust</h4>
            <ul className="issues-list">{(strengths.brand_domain_trust || []).map((s, i) => <li key={i} className="issue"><span className="issue-text">{s}</span></li>)}</ul>
          </div>
          <div>
            <h4>Navigation & Layout</h4>
            <ul className="issues-list">{(strengths.navigation_layout || []).map((s, i) => <li key={i} className="issue"><span className="issue-text">{s}</span></li>)}</ul>
          </div>
          <div>
            <h4>Technical Signals</h4>
            <ul className="issues-list">{(strengths.technical_signals || []).map((s, i) => <li key={i} className="issue"><span className="issue-text">{s}</span></li>)}</ul>
          </div>
        </div>
      </section>

      <section className="issues-summary">
        <h3>Weaknesses</h3>
        <div className="two-col">
          <div>
            <h4>Content Depth</h4>
            <ul className="issues-list">{(weaknesses.content_depth || []).map((w, i) => <li key={i} className="issue"><span className="issue-text">{w}</span></li>)}</ul>
          </div>
          <div>
            <h4>Authority & Trust</h4>
            <ul className="issues-list">{(weaknesses.authority_trust || []).map((w, i) => <li key={i} className="issue"><span className="issue-text">{w}</span></li>)}</ul>
          </div>
          <div>
            <h4>Semantic & Accessibility</h4>
            <ul className="issues-list">{(weaknesses.semantic_accessibility || []).map((w, i) => <li key={i} className="issue"><span className="issue-text">{w}</span></li>)}</ul>
          </div>
          <div>
            <h4>UX Friction</h4>
            <ul className="issues-list">{(weaknesses.ux_friction || []).map((w, i) => <li key={i} className="issue"><span className="issue-text">{w}</span></li>)}</ul>
          </div>
        </div>
      </section>

      <section className="issues-summary">
        <h3>Implications for AEO</h3>
        <p>{implications.overview}</p>
        <ul className="issues-list">{(implications.bullets || []).map((b, i) => <li key={i} className="issue"><span className="issue-text">{b}</span></li>)}</ul>
      </section>

      <section className="issues-summary">
        <h3>Recommendations</h3>
        {recommendations.length > 0 ? (
          <ul className="issues-list">
            {recommendations.map((rec, i) => (
              <li key={i} className="issue">
                <span className="issue-text"><strong>[{rec.priority?.toUpperCase?.() || rec.priority}]</strong> {rec.action}</span>
                <div className="meta-inline">Owner: {rec.owner} • Effort: {rec.effort} • Impact: {rec.impact}</div>
                {rec.rationale && <div className="small-note">Why: {rec.rationale}</div>}
                {Array.isArray(rec.success_metrics) && rec.success_metrics.length > 0 && (
                  <div className="small-note">Success: {rec.success_metrics.join(', ')}</div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p>No recommendations.</p>
        )}
      </section>

      <section className="issues-summary">
        <h3>Quick Win Checklist</h3>
        {checklist.length > 0 ? (
          <ul className="issues-list">
            {checklist.map((c, i) => (
              <li key={i} className="issue">
                <span className="issue-text">{c.action}</span>
                <div className="meta-inline">Status: {c.status} • Target: {c.target_metric}</div>
                {c.why_it_matters && <div className="small-note">{c.why_it_matters}</div>}
              </li>
            ))}
          </ul>
        ) : (
          <p>No checklist items.</p>
        )}
      </section>

      <section className="issues-summary">
        <h3>Analyzed Pages</h3>
        {pageScores.length > 0 ? (
          <ul className="issues-list">
            {pageScores.map((pr, index) => (
              <li key={index} className="issue">
                <span className="issue-text">
                  <a href={pr.url} target="_blank" rel="noreferrer">{pr.url}</a>
                </span>
                <span className="issue-priority">{pr.score}/100</span>
                {Array.isArray(pr.key_observations) && pr.key_observations.length > 0 && (
                  <ul className="sub-list">
                    {pr.key_observations.map((o, j) => (
                      <li key={j} className="issue"><span className="issue-text">{o}</span></li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p>No page-level details available.</p>
        )}
      </section>

      <section className="issues-summary">
        <h3>Bottom Line</h3>
        <p>{reportData.bottom_line}</p>
      </section>

      <section className="issues-summary">
        <h3>A/B Testing Plan</h3>
        {abTests.length > 0 ? (
          <ul className="issues-list">
            {abTests.map((t, i) => (
              <li key={i} className="issue">
                <span className="issue-text"><strong>Hypothesis:</strong> {t.hypothesis}</span>
                <div className="small-note">Changes: {(t.variant_changes || []).join(', ')}</div>
                <div className="meta-inline">Primary: {t.primary_metric} • Secondary: {(t.secondary_metrics || []).join(', ')} • Duration: {t.duration_weeks} weeks</div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No A/B tests proposed.</p>
        )}
      </section>

      <section className="issues-summary">
        <h3>KPIs to Monitor</h3>
        <ul className="issues-list">{(kpis || []).map((k, i) => <li key={i} className="issue"><span className="issue-text">{k}</span></li>)}</ul>
      </section>

      <div className="action-buttons">
        <h3>How would you like to proceed?</h3>
        <div className="button-group">
          <button className="diy-button" onClick={onChooseDIY}>
            <span className="button-icon">🔍</span>
            <span className="button-text">
              <strong>View Details</strong>
              <small>See page scores and summary</small>
            </span>
          </button>
          
          <button className="hire-button" onClick={onChooseHire}>
            <span className="button-icon">👨‍💼</span>
            <span className="button-text">
              <strong>Hire an Expert</strong>
              <small>Let professionals handle it</small>
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};

// Steps workflow removed

// Hire Form Component (Step 8)
const HireForm = ({ url, email, onSubmit, onBack, loading, error, success }) => {
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    website: url || '',
    phone: '',
    message: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...formData, email });
  };

  if (success) {
    return (
      <div className="form-container">
        <div className="success-container">
          <div className="success-icon">✅</div>
          <h2>Request Submitted!</h2>
          <p>Thanks for your interest! Our team will reach out to you shortly.</p>
          <button className="back-button" onClick={onBack}>
            ← Back to Report
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="form-container hire-container">
      <h2>Hire AI Experts</h2>
      <p className="subtitle">Tell us about your project and we'll get back to you</p>
      
      <form onSubmit={handleSubmit} className="hire-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="name">Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Your full name"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="company">Company</label>
            <input
              type="text"
              id="company"
              name="company"
              value={formData.company}
              onChange={handleChange}
              placeholder="Company name"
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="website">Website</label>
          <input
            type="url"
            id="website"
            name="website"
            value={formData.website}
            onChange={handleChange}
            placeholder="https://yourwebsite.com"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="phone">Phone (optional)</label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+1 (555) 123-4567"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="message">Tell us about your project</label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            rows="4"
            placeholder="Describe your AI readiness goals and any specific challenges..."
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="button-group">
          <button 
            type="submit" 
            className="submit-button" 
            disabled={loading || !formData.name.trim()}
          >
            {loading ? 'Submitting...' : 'Submit Request'}
          </button>
          
          <button 
            type="button" 
            className="cancel-button" 
            onClick={onBack}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

// Main App Component
function App() {
  const { preferences } = useConsent();
  const [currentStep, setCurrentStep] = useState('urlInput');
  const [url, setUrl] = useState('');
  const [analysisId, setAnalysisId] = useState(null);
  const [score, setScore] = useState(null);
  const [analyzedUrl, setAnalyzedUrl] = useState('');
  const [quickCategories, setQuickCategories] = useState(null);
  const [email, setEmail] = useState('');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Reset to home function
  const resetToHome = () => {
    setCurrentStep('urlInput');
    setUrl('');
    setAnalysisId(null);
    setScore(null);
    setAnalyzedUrl('');
    setEmail('');
    setReportData(null);
    setLoading(false);
    setError('');
    setSuccess('');
  };

  // API call function
  const apiCall = async (endpoint, method = 'GET', body = null) => {
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
          // Forward consent to backend so it can honor opt-out regardless of cookies/origin
          'X-Consent-Do-Not-Sell': preferences?.doNotSell ? '1' : '0',
          'X-Consent-Functional': preferences?.functional ? '1' : '0',
          'X-Consent-Analytics': preferences?.analytics ? '1' : '0',
          'X-Consent-Marketing': preferences?.marketing ? '1' : '0',
          // Forward GPC where supported
          'Sec-GPC': (typeof navigator !== 'undefined' && navigator.globalPrivacyControl) ? '1' : '0',
        },
      };
      
      if (body) {
        options.body = JSON.stringify(body);
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
      }
      
      return data;
    } catch (err) {
      throw new Error(err.message || 'Network error. Make sure the backend is running.');
    }
  };

  // Step 1: Handle URL analysis
  const handleAnalyze = async (inputUrl) => {
    setLoading(true);
    setError('');
    setUrl(inputUrl);
    
    try {
      const result = await apiCall('/analyze/quick', 'POST', { url: inputUrl });
      // New structured response
      setScore(result.overall_score);
      setAnalyzedUrl(result.url || inputUrl);
      setQuickCategories({
        content_quality: result.content_quality,
        structure_optimization: result.structure_optimization,
        authority_trust: result.authority_trust,
      });
      // no summary in new quick response
      setAnalysisId(result.analysis_id);
      setCurrentStep('quickGrade');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Handle report request
  const handleRequestReport = async (userEmail) => {
    setLoading(true);
    setError('');
    setEmail(userEmail);
    
    try {
      await apiCall('/report/request', 'POST', { url, email: userEmail });
      setSuccess('Verification code sent to your email.');
      setCurrentStep('verifyEmail');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Handle email verification
  const handleVerifyEmail = async (code) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await apiCall('/auth/verify-email', 'POST', { email, code });
      setSuccess('Email verified! Generating your report...');
      
      // Fetch the detailed report (now includes page_results and summary)
      const report = await apiCall(`/report/${analysisId}`);
      setReportData(report);
      setCurrentStep('detailedReport');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle resend verification code
  const handleResendCode = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await apiCall('/resend-verification', 'POST', { email });
      setSuccess('Verification code sent! Check your console.');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Steps removed

  // Step 8: Handle hire form submission
  const handleHireSubmit = async (hireData) => {
    setLoading(true);
    setError('');
    
    try {
      await apiCall('/hire/request', 'POST', {
        ...hireData,
        site_id: analysisId
      });
      setSuccess('Hire request submitted successfully!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Navigation helpers
  const goToReport = () => setCurrentStep('detailedReport');
  const goToDIY = () => setCurrentStep('detailedReport');
  const goToHire = () => setCurrentStep('hireForm');

  // Render current step
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'urlInput':
        return (
          <UrlInputForm 
            onAnalyze={handleAnalyze}
            loading={loading}
            error={error}
          />
        );
      case 'quickGrade':
        return (
          <QuickGradeResult 
            score={score}
            url={analyzedUrl}
            categories={quickCategories}
            onRequestReport={handleRequestReport}
            loading={loading}
            error={error}
          />
        );
      case 'verifyEmail':
        return (
          <EmailVerificationForm 
            email={email}
            onVerify={handleVerifyEmail}
            onResend={handleResendCode}
            loading={loading}
            error={error}
            success={success}
          />
        );
      case 'detailedReport':
        return (
          <DetailedReport 
            reportData={reportData}
            onChooseDIY={goToDIY}
            onChooseHire={goToHire}
            loading={loading}
          />
        );
      // steps workflow removed
      case 'hireForm':
        return (
          <HireForm 
            url={url}
            email={email}
            onSubmit={handleHireSubmit}
            onBack={goToReport}
            loading={loading}
            error={error}
            success={success}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="App">
      <Header onLogoClick={resetToHome} />
      <main className="App-main">
        {renderCurrentStep()}
      </main>
      <Footer />
    </div>
  );
}

export default App; 