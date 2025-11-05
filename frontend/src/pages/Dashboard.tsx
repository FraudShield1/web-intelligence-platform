import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMetrics();
    // Poll every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/analytics/dashboard?date_range=7d');
      setMetrics(response.data);
      setError('');
    } catch (err: any) {
      setError('Failed to load metrics: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-body">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-body">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="page-body">
      <div className="page-header" style={{ background: 'transparent', border: 'none', paddingBottom: 0 }}>
        <h1 className="page-title">Dashboard</h1>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-4">
        <div className="metric-card">
          <div className="metric-label">Total Sites</div>
          <div className="metric-value">{metrics?.total_sites || 0}</div>
          <div className="metric-trend">+{metrics?.sites_new || 0} this week</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Ready to Scrape</div>
          <div className="metric-value">{metrics?.sites_ready || 0}</div>
          <div className="metric-trend">{((metrics?.sites_ready || 0) / (metrics?.total_sites || 1) * 100).toFixed(0)}% of total</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Success Rate</div>
          <div className="metric-value">{((metrics?.discovery_metrics?.success_rate || 0) * 100).toFixed(1)}%</div>
          <div className="metric-trend">Last 7 days</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Avg Discovery Time</div>
          <div className="metric-value">{(metrics?.discovery_metrics?.avg_discovery_time_seconds || 0).toFixed(0)}s</div>
          <div className="metric-trend">Per site</div>
        </div>
      </div>

      {/* Status Distribution */}
      <div className="grid grid-cols-2">
        <div className="card">
          <div className="card-title">Sites by Status</div>
          <table className="table">
            <tbody>
              {Object.entries(metrics?.site_distribution?.by_status || {}).map(([status, count]: [string, any]) => (
                <tr key={status}>
                  <td>
                    <span className={`badge badge-${status}`}>{status}</span>
                  </td>
                  <td style={{ textAlign: 'right', fontWeight: 'bold' }}>{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="card-title">Sites by Platform</div>
          <table className="table">
            <tbody>
              {Object.entries(metrics?.site_distribution?.by_platform || {}).map(([platform, count]: [string, any]) => (
                <tr key={platform}>
                  <td>{platform}</td>
                  <td style={{ textAlign: 'right', fontWeight: 'bold' }}>{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quality Metrics */}
      <div className="card">
        <div className="card-title">Quality Metrics</div>
        <div className="grid grid-cols-3">
          <div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
              Avg Blueprint Confidence
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
              {(metrics?.quality_metrics?.avg_blueprint_confidence || 0).toFixed(2)}
            </div>
          </div>
          <div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
              Selector Failure Rate
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
              {(metrics?.quality_metrics?.selector_failure_rate || 0).toFixed(2)}
            </div>
          </div>
          <div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
              Avg Categories Found
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
              {metrics?.quality_metrics?.categories_average || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Discovery Stats */}
      <div className="card">
        <div className="card-title">Discovery Statistics (Last 7 Days)</div>
        <div className="grid grid-cols-3">
          <div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
              Total Discoveries
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
              {metrics?.discovery_metrics?.total_discoveries || 0}
            </div>
          </div>
          <div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
              Successful
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>
              {metrics?.discovery_metrics?.successful_discoveries || 0}
            </div>
          </div>
          <div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
              Failed
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#ef4444' }}>
              {(metrics?.discovery_metrics?.total_discoveries || 0) - (metrics?.discovery_metrics?.successful_discoveries || 0)}
            </div>
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', color: '#6b7280', fontSize: '0.875rem', marginTop: '2rem' }}>
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default Dashboard;

