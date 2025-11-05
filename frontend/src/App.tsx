import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Sites from './pages/Sites';
import Jobs from './pages/Jobs';
import Analytics from './pages/Analytics';
import './App.css';

// Set default API base URL - HARDCODED for Vercel deployment
// Updated: Force Vercel rebuild with Railway backend URL
const API_URL = 'https://web-intelligence-platform-production.up.railway.app/api/v1';
axios.defaults.baseURL = API_URL;

// Debug: Log the API URL
console.log('API Base URL:', axios.defaults.baseURL);
console.log('Environment VITE_API_URL:', import.meta.env.VITE_API_URL);

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Navbar />
        <div className="app-container">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/sites" element={<Sites />} />
              <Route path="/jobs" element={<Jobs />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;

