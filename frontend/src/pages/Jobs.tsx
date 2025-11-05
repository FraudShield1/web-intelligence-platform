import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Jobs = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ status: '', job_type: '' });

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [filter]);

  const fetchJobs = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.status) params.append('status', filter.status);
      if (filter.job_type) params.append('job_type', filter.job_type);
      params.append('limit', '50');

      const response = await axios.get(`/jobs?${params}`);
      setJobs(response.data.jobs);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const cancelJob = async (jobId: string) => {
    try {
      await axios.post(`/jobs/${jobId}/cancel`);
      fetchJobs();
    } catch (err) {
      alert('Failed to cancel job');
    }
  };

  const retryJob = async (jobId: string) => {
    try {
      await axios.post(`/jobs/${jobId}/retry`);
      fetchJobs();
    } catch (err) {
      alert('Failed to retry job');
    }
  };

  const getProgressBar = (status: string) => {
    let percentage = 0;
    let color = '#3b82f6';

    switch (status) {
      case 'queued':
        percentage = 10;
        color = '#f59e0b';
        break;
      case 'running':
        percentage = 50;
        color = '#3b82f6';
        break;
      case 'success':
        percentage = 100;
        color = '#10b981';
        break;
      case 'failed':
        percentage = 100;
        color = '#ef4444';
        break;
      default:
        percentage = 0;
    }

    return (
      <div style={{
        width: '100px',
        height: '8px',
        backgroundColor: '#e5e7eb',
        borderRadius: '4px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${percentage}%`,
          height: '100%',
          backgroundColor: color,
          transition: 'width 0.3s ease'
        }}></div>
      </div>
    );
  };

  return (
    <div className="page-body">
      <div className="page-header" style={{ background: 'transparent', border: 'none', paddingBottom: 0 }}>
        <h1 className="page-title">Jobs</h1>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-title">Filters</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Status</label>
            <select
              className="form-input"
              value={filter.status}
              onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            >
              <option value="">All</option>
              <option value="queued">Queued</option>
              <option value="running">Running</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Job Type</label>
            <select
              className="form-input"
              value={filter.job_type}
              onChange={(e) => setFilter({ ...filter, job_type: e.target.value })}
            >
              <option value="">All</option>
              <option value="fingerprint">Fingerprint</option>
              <option value="discovery">Discovery</option>
              <option value="extraction">Extraction</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">&nbsp;</label>
            <button
              type="button"
              className="button button-secondary"
              onClick={() => { setFilter({ status: '', job_type: '' }); }}
              style={{ width: '100%' }}
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Jobs Table */}
      <div className="card">
        <div className="card-title">Active Jobs</div>
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : jobs.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Type</th>
                <th>Method</th>
                <th>Status</th>
                <th>Progress</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.job_id}>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                    {job.job_id.substring(0, 8)}...
                  </td>
                  <td>{job.job_type}</td>
                  <td>{job.method || '-'}</td>
                  <td>
                    <span className={`badge badge-${job.status}`}>{job.status}</span>
                  </td>
                  <td>{getProgressBar(job.status)}</td>
                  <td style={{ fontSize: '0.875rem' }}>
                    {new Date(job.created_at).toLocaleTimeString()}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {job.status === 'running' && (
                        <button
                          className="button button-danger"
                          onClick={() => cancelJob(job.job_id)}
                          style={{ fontSize: '0.7rem', padding: '0.2rem 0.4rem' }}
                        >
                          Cancel
                        </button>
                      )}
                      {job.status === 'failed' && (
                        <button
                          className="button button-success"
                          onClick={() => retryJob(job.job_id)}
                          style={{ fontSize: '0.7rem', padding: '0.2rem 0.4rem' }}
                        >
                          Retry
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
            No jobs found
          </div>
        )}
      </div>

      <div style={{ textAlign: 'center', color: '#6b7280', fontSize: '0.875rem', marginTop: '1rem' }}>
        Updates every 5 seconds • Last: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default Jobs;

