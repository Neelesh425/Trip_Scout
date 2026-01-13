import React from 'react';
import { useNavigate } from 'react-router-dom';
import './index.scss';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/home');
  };

  return (
    <div className="landing-page">
      <div className="landing-content">
        <div className="hero-section">
          <div className="floating-elements">
            <div className="float-item plane">✈️</div>
            <div className="float-item world">🌍</div>
            <div className="float-item compass">🧭</div>
          </div>
          
          <h1 className="main-title">
            Your Journey
            <span className="gradient-text"> Begins Here</span>
          </h1>
          
          <p className="subtitle">
            Discover extraordinary destinations with our Travel Planning Agent.
            Your perfect adventure awaits.
          </p>
          
          <button className="cta-button" onClick={handleGetStarted}>
            <span>Get Started</span>
            <svg className="arrow" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          
          <div className="features">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI-Powered</h3>
              <p>Smart recommendations tailored to you</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Lightning Fast</h3>
              <p>Instant search and planning</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🗺️</div>
              <h3>Global Reach</h3>
              <p>Explore destinations worldwide</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="background-gradient"></div>
      <div className="grid-overlay"></div>
    </div>
  );
};

export default LandingPage;