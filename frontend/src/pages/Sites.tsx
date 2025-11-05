import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Sites = () => {
  const [sites, setSites] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [domain, setDomain] = useState('');
  const [filter, setFilter] = useState({ status: '', platform: '' });
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchSites();
  }, [filter]);

  const fetchSites = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter.status) params.append('status', filter.status);
      if (filter.platform) params.append('platform', filter.platform);
      
      const response = await axios.get(`/sites?${params}`);
      setSites(response.data.sites);
      setTotal(response.data.total);
    } catch (err) {
      console.error('Failed to fetch sites:', err);
    } finally {
      setLoading(false);
    }
  };

  const addSite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!domain.trim()) return;

    try {
      await axios.post('/sites', { domain: domain.trim() });
      setDomain('');
      fetchSites();
    } catch (err: any) {
      alert('Failed to add site: ' + (err.response?.data?.detail || err.message));
    }
  };

  const deleteSite = async (siteId: string) => {
    if (!window.confirm('Are you sure?')) return;
    try {
      await axios.delete(`/sites/${siteId}`);
      fetchSites();
    } catch (err) {
      alert('Failed to delete site');
    }
  };

  return (
    <div className="page-body">
      <div className="page-header" style={{ background: 'transparent', border: 'none', paddingBottom: 0 }}>
        <h1 className="page-title">Sites</h1>
      </div>

      {/* Add Site Form */}
      <div className="card">
        <div className="card-title">Add New Site</div>
        <form onSubmit={addSite} style={{ display: 'flex', gap: '1rem' }}>
          <input
            type="text"
            placeholder="e.g., example.com"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="form-input"
            style={{ flex: 1 }}
          />
          <button type="submit" className="button button-primary">
            Add Site
          </button>
        </form>
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
              <option value="pending">Pending</option>
              <option value="ready">Ready</option>
              <option value="review">Review</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Platform</label>
            <select
              className="form-input"
              value={filter.platform}
              onChange={(e) => setFilter({ ...filter, platform: e.target.value })}
            >
              <option value="">All</option>
              <option value="shopify">Shopify</option>
              <option value="magento">Magento</option>
              <option value="woocommerce">WooCommerce</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">&nbsp;</label>
            <button
              type="button"
              className="button button-secondary"
              onClick={() => { setFilter({ status: '', platform: '' }); }}
              style={{ width: '100%' }}
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Sites Table */}
      <div className="card">
        <div className="card-title">
          Sites ({loading ? '...' : total})
        </div>
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : sites.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Domain</th>
                <th>Platform</th>
                <th>Status</th>
                <th>Complexity</th>
                <th>Value</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sites.map((site) => (
                <tr key={site.site_id}>
                  <td style={{ fontFamily: 'monospace' }}>{site.domain}</td>
                  <td>{site.platform || '-'}</td>
                  <td>
                    <span className={`badge badge-${site.status}`}>{site.status}</span>
                  </td>
                  <td>{site.complexity_score ? (site.complexity_score * 100).toFixed(0) + '%' : '-'}</td>
                  <td>{site.business_value_score ? (site.business_value_score * 100).toFixed(0) + '%' : '-'}</td>
                  <td style={{ fontSize: '0.875rem' }}>
                    {new Date(site.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <button
                      className="button button-danger"
                      onClick={() => deleteSite(site.site_id)}
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
            No sites found. Add one to get started!
          </div>
        )}
      </div>
    </div>
  );
};

export default Sites;

