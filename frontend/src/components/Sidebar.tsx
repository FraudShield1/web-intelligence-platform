import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <div className="sidebar">
      <ul className="sidebar-menu">
        <li className="sidebar-item">
          <Link 
            to="/" 
            className={`sidebar-link ${isActive('/') ? 'active' : ''}`}
          >
            📊 Dashboard
          </Link>
        </li>
        <li className="sidebar-item">
          <Link 
            to="/sites" 
            className={`sidebar-link ${isActive('/sites') ? 'active' : ''}`}
          >
            🌍 Sites
          </Link>
        </li>
        <li className="sidebar-item">
          <Link 
            to="/jobs" 
            className={`sidebar-link ${isActive('/jobs') ? 'active' : ''}`}
          >
            ⚙️ Jobs
          </Link>
        </li>
        <li className="sidebar-item">
          <Link 
            to="/analytics" 
            className={`sidebar-link ${isActive('/analytics') ? 'active' : ''}`}
          >
            📈 Analytics
          </Link>
        </li>
        <li className="sidebar-item">
          <Link 
            to="/templates" 
            className={`sidebar-link ${isActive('/templates') ? 'active' : ''}`}
          >
            📋 Templates
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;

