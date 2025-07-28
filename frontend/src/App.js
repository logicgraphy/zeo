import React, { useState } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

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
      <h2>Get Your Instant SEO Grade</h2>
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
        
        <button 
          type="submit" 
          className="analyze-button" 
          disabled={loading || !url.trim() || !isValidUrl(url)}
        >
          {loading ? 'Analyzing...' : 'Analyze Website'}
        </button>
      </form>
      
      <p className="help-text">
        Get instant insights about your website's SEO performance
      </p>
    </div>
  );
};

// Quick Grade Result Component (Step 2)
const QuickGradeResult = ({ grade, summary, onRequestReport, loading, error }) => {
  const [email, setEmail] = useState('');
  const [showEmailForm, setShowEmailForm] = useState(false);

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    if (email.trim()) {
      onRequestReport(email.trim());
    }
  };

  const getGradeColor = (grade) => {
    if (grade >= 90) return '#4CAF50'; // Green
    if (grade >= 70) return '#FF9800'; // Orange  
    if (grade >= 50) return '#FF5722'; // Red-Orange
    return '#F44336'; // Red
  };

  const getGradeLetter = (grade) => {
    if (grade >= 90) return 'A';
    if (grade >= 80) return 'B';
    if (grade >= 70) return 'C';
    if (grade >= 60) return 'D';
    return 'F';
  };

  return (
    <div className="form-container">
      <h2>Your SEO Grade</h2>
      
      <div className="grade-display">
        <div className="grade-circle" style={{ borderColor: getGradeColor(grade) }}>
          <span className="grade-letter" style={{ color: getGradeColor(grade) }}>
            {getGradeLetter(grade)}
          </span>
          <span className="grade-number">{grade}/100</span>
        </div>
      </div>
      
      <div className="summary-box">
        <p>{summary}</p>
      </div>

      {!showEmailForm ? (
        <div className="email-prompt">
          <h3>Want a detailed report?</h3>
          <p>Enter your email to receive a comprehensive SEO analysis</p>
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
      </form>
      
      <p className="help-text">
        Check your console for the verification code (demo mode)
      </p>
    </div>
  );
};

// Detailed Report Component (Step 5 & 6)
const DetailedReport = ({ reportData, onChooseDIY, onChooseHire, loading }) => {
  if (loading) {
    return (
      <div className="form-container">
        <h2>Generating Your Report</h2>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Analyzing your website in detail...</p>
        </div>
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

  return (
    <div className="form-container report-container">
      <h2>Detailed SEO Report</h2>
      
      <div className="report-summary">
        <div className="score-display">
          <h3>Overall Score: {reportData.score}/100</h3>
        </div>
        
        {reportData.report_url && (
          <div className="report-link">
            <a href={reportData.report_url} target="_blank" rel="noopener noreferrer">
              View Full Report
            </a>
          </div>
        )}
      </div>

      <div className="issues-summary">
        <h3>Key Issues Found</h3>
        {reportData.issues && reportData.issues.length > 0 ? (
          <ul className="issues-list">
            {reportData.issues.slice(0, 5).map((issue, index) => (
              <li key={index} className={`issue issue-${issue.priority}`}>
                <span className="issue-text">{issue.text}</span>
                <span className="issue-priority">{issue.priority}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p>Great! No major issues found.</p>
        )}
      </div>

      <div className="action-buttons">
        <h3>How would you like to proceed?</h3>
        <div className="button-group">
          <button className="diy-button" onClick={onChooseDIY}>
            <span className="button-icon">🔧</span>
            <span className="button-text">
              <strong>Fix it Myself</strong>
              <small>Get step-by-step guidance</small>
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

// DIY Steps Component (Step 7)
const DIYSteps = ({ steps, onUpdateStep, onBack, loading }) => {
  const groupedSteps = {
    high: steps.filter(step => step.priority === 'high'),
    medium: steps.filter(step => step.priority === 'medium'),
    low: steps.filter(step => step.priority === 'low')
  };

  const handleStepToggle = (stepId, completed) => {
    onUpdateStep(stepId, completed);
  };

  const priorityLabels = {
    high: { label: 'High Priority', color: '#F44336' },
    medium: { label: 'Medium Priority', color: '#FF9800' },
    low: { label: 'Low Priority', color: '#4CAF50' }
  };

  return (
    <div className="form-container diy-container">
      <h2>DIY SEO Improvement Guide</h2>
      <p className="subtitle">Follow these steps to improve your website's SEO</p>
      
      {Object.entries(groupedSteps).map(([priority, prioritySteps]) => (
        prioritySteps.length > 0 && (
          <div key={priority} className="priority-section">
            <h3 
              className="priority-header"
              style={{ color: priorityLabels[priority].color }}
            >
              {priorityLabels[priority].label} ({prioritySteps.length} items)
            </h3>
            
            <div className="steps-list">
              {prioritySteps.map(step => (
                <div key={step.id} className="step-item">
                  <label className="step-checkbox">
                    <input
                      type="checkbox"
                      checked={step.completed}
                      onChange={(e) => handleStepToggle(step.id, e.target.checked)}
                      disabled={loading}
                    />
                    <span className="checkmark"></span>
                  </label>
                  
                  <div className={`step-content ${step.completed ? 'completed' : ''}`}>
                    <p className="step-text">{step.step_text}</p>
                    {step.impact && (
                      <p className="step-impact">Expected Impact: {step.impact}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      ))}
      
      <div className="action-buttons">
        <button className="download-button">
          📄 Download as PDF
        </button>
        <button className="back-button" onClick={onBack}>
          ← Back to Report
        </button>
      </div>
    </div>
  );
};

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
      <h2>Hire SEO Experts</h2>
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
            placeholder="Describe your SEO goals and any specific challenges..."
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
  const [currentStep, setCurrentStep] = useState('urlInput');
  const [url, setUrl] = useState('');
  const [analysisId, setAnalysisId] = useState(null);
  const [grade, setGrade] = useState(null);
  const [summary, setSummary] = useState('');
  const [email, setEmail] = useState('');
  const [reportData, setReportData] = useState(null);
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // API call function
  const apiCall = async (endpoint, method = 'GET', body = null) => {
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
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
      setGrade(result.grade);
      setSummary(result.summary);
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
      
      // Fetch the detailed report
      const report = await apiCall(`/report/${analysisId}`);
      setReportData(report);
      
      // Fetch DIY steps
      const stepsResult = await apiCall(`/report/${analysisId}/steps`);
      setSteps(stepsResult.steps || []);
      
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

  // Step 7: Handle step completion update
  const handleUpdateStep = async (stepId, completed) => {
    try {
      const updatedStep = await apiCall(`/steps/${stepId}`, 'PATCH', { completed });
      setSteps(steps.map(step => 
        step.id === stepId ? { ...step, completed: updatedStep.completed } : step
      ));
    } catch (err) {
      setError(err.message);
    }
  };

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
  const goToDIY = () => setCurrentStep('diySteps');
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
            grade={grade}
            summary={summary}
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
      case 'diySteps':
        return (
          <DIYSteps 
            steps={steps}
            onUpdateStep={handleUpdateStep}
            onBack={goToReport}
            loading={loading}
          />
        );
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

  const getStepNumber = () => {
    const stepMap = {
      'urlInput': 1,
      'quickGrade': 2,
      'verifyEmail': 3,
      'detailedReport': 4,
      'diySteps': 5,
      'hireForm': 5
    };
    return stepMap[currentStep] || 1;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>SEO Analyzer</h1>
        <div className="step-indicator">
          <div className={`step ${getStepNumber() >= 1 ? 'completed' : ''} ${getStepNumber() === 1 ? 'active' : ''}`}>
            1. Analyze
          </div>
          <div className={`step ${getStepNumber() >= 2 ? 'completed' : ''} ${getStepNumber() === 2 ? 'active' : ''}`}>
            2. Grade
          </div>
          <div className={`step ${getStepNumber() >= 3 ? 'completed' : ''} ${getStepNumber() === 3 ? 'active' : ''}`}>
            3. Verify
          </div>
          <div className={`step ${getStepNumber() >= 4 ? 'completed' : ''} ${getStepNumber() === 4 ? 'active' : ''}`}>
            4. Report
          </div>
          <div className={`step ${getStepNumber() >= 5 ? 'completed' : ''} ${getStepNumber() === 5 ? 'active' : ''}`}>
            5. Action
          </div>
        </div>
        {renderCurrentStep()}
      </header>
    </div>
  );
}

export default App; 