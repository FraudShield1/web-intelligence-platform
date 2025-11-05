import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Analytics = () => {
  const [performance, setPerformance] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('/analytics/methods/performance');
      setPerformance(response.data);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-body">
      <div className="page-header" style={{ background: 'transparent', border: 'none', paddingBottom: 0 }}>
        <h1 className="page-title">Analytics</h1>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      ) : (
        <>
          {/* Method Performance */}
          <div className="card">
            <div className="card-title">Discovery Method Performance</div>
            <table className="table">
              <thead>
                <tr>
                  <th>Method</th>
                  <th>Total Jobs</th>
                  <th>Success Rate</th>
                  <th>Avg Time (s)</th>
                  <th>Avg Cost ($)</th>
                </tr>
              </thead>
              <tbody>
                {performance?.method_performance?.map((method: any) => (
                  <tr key={method.method}>
                    <td style={{ fontWeight: 'bold' }}>{method.method}</td>
                    <td>{method.total_jobs}</td>
                    <td>
                      <span style={{
                        color: method.success_rate > 0.9 ? '#10b981' : method.success_rate > 0.7 ? '#f59e0b' : '#ef4444',
                        fontWeight: 'bold'
                      }}>
                        {(method.success_rate * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td>{method.avg_time_seconds.toFixed(1)}</td>
                    <td>${method.avg_cost_usd.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Recommendations */}
          <div className="card">
            <div className="card-title">Recommendations</div>
            <ul style={{ paddingLeft: '1.5rem' }}>
              {performance?.recommendations?.map((rec: string, idx: number) => (
                <li key={idx} style={{ marginBottom: '0.5rem', color: '#1f2937' }}>
                  ✨ {rec}
                </li>
              ))}
            </ul>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-3">
            <div className="card">
              <div className="metric-label">Avg Success Rate</div>
              <div className="metric-value">
                {(
                  (performance?.method_performance?.reduce((sum: number, m: any) => sum + m.success_rate, 0) || 0) /
                  (performance?.method_performance?.length || 1) * 100
                ).toFixed(1)}%
              </div>
            </div>
            <div className="card">
              <div className="metric-label">Most Used Method</div>
              <div className="metric-value">
                {performance?.method_performance?.reduce((max: any, m: any) => 
                  (m.total_jobs > (max?.total_jobs || 0) ? m : max), null)?.method || 'N/A'
                }
              </div>
            </div>
            <div className="card">
              <div className="metric-label">Total Jobs Processed</div>
              <div className="metric-value">
                {performance?.method_performance?.reduce((sum: number, m: any) => sum + m.total_jobs, 0) || 0}
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="card">
            <div className="card-title">Method Details</div>
            <div className="grid grid-cols-2">
              {performance?.method_performance?.map((method: any) => (
                <div key={method.method} style={{ padding: '1rem', borderRight: '1px solid #e5e7eb' }}>
                  <h3 style={{ fontWeight: 'bold', marginBottom: '0.5rem', textTransform: 'capitalize' }}>
                    {method.method} Method
                  </h3>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    <div>Total Jobs: <strong>{method.total_jobs}</strong></div>
                    <div>Successful: <strong>{method.success_count}</strong></div>
                    <div>Success Rate: <strong>{(method.success_rate * 100).toFixed(1)}%</strong></div>
                    <div>Avg Duration: <strong>{method.avg_time_seconds.toFixed(1)}s</strong></div>
                    <div>Cost per Job: <strong>${method.avg_cost_usd.toFixed(2)}</strong></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Analytics;

