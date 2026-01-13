import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import './index.scss';

const ProfilePage = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    fullName: user?.full_name || '',
    email: user?.email || ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement profile update API call
    alert('Profile update feature coming soon!');
    setIsEditing(false);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1>My Profile</h1>
        <p>Manage your account settings</p>
      </div>

      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {user?.full_name?.charAt(0).toUpperCase()}
            </div>
          </div>

          <div className="profile-info">
            {!isEditing ? (
              <>
                <div className="info-group">
                  <label>Full Name</label>
                  <p>{user?.full_name}</p>
                </div>

                <div className="info-group">
                  <label>Email</label>
                  <p>{user?.email}</p>
                </div>

                <div className="info-group">
                  <label>Account Status</label>
                  <p>
                    <span className="status-badge active">
                      {user?.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </p>
                </div>

                <div className="info-group">
                  <label>Member Since</label>
                  <p>{user?.created_at ? formatDate(user.created_at) : 'N/A'}</p>
                </div>

                <button 
                  className="btn btn-primary"
                  onClick={() => setIsEditing(true)}
                >
                  Edit Profile
                </button>
              </>
            ) : (
              <form onSubmit={handleSubmit} className="edit-form">
                <div className="form-group">
                  <label htmlFor="fullName">Full Name</label>
                  <input
                    type="text"
                    id="fullName"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-actions">
                  <button type="submit" className="btn btn-primary">
                    Save Changes
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => setIsEditing(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>

        <div className="account-stats">
          <h3>Account Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">🔍</div>
              <div className="stat-value">0</div>
              <div className="stat-label">Searches</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📋</div>
              <div className="stat-value">0</div>
              <div className="stat-label">Bookings</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">✈️</div>
              <div className="stat-value">0</div>
              <div className="stat-label">Trips Planned</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;