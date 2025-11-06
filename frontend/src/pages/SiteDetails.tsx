import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

interface SiteDetail {
  site_id: string;
  domain: string;
  platform: string | null;
  status: string;
  complexity_score: number | null;
  business_value_score: number | null;
  blueprint_version: number;
  created_at: string;
  updated_at: string;
  last_discovered_at: string | null;
  fingerprint_data: any;
  notes: string | null;
  created_by: string | null;
}

interface Blueprint {
  blueprint_id: string;
  site_id: string;
  version: number;
  confidence_score: number | null;
  categories_data: any;
  endpoints_data: any;
  render_hints_data: any;
  selectors_data: any;
  created_at: string;
  created_by: string | null;
  notes: string | null;
}

const SiteDetails = () => {
  const { siteId } = useParams<{ siteId: string }>();
  const navigate = useNavigate();
  const [site, setSite] = useState<SiteDetail | null>(null);
  const [blueprints, setBlueprints] = useState<Blueprint[]>([]);
  const [selectedBlueprint, setSelectedBlueprint] = useState<Blueprint | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'fingerprint' | 'blueprint'>('overview');

  useEffect(() => {
    if (siteId) {
      fetchSiteDetails();
      fetchBlueprints();
    }
  }, [siteId]);

  const fetchSiteDetails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/sites/${siteId}`);
      setSite(response.data);
      setError('');
    } catch (err: any) {
      console.error('Failed to fetch site details:', err);
      setError(err.response?.data?.detail || 'Failed to load site details');
    } finally {
      setLoading(false);
    }
  };

  const fetchBlueprints = async () => {
    try {
      const response = await axios.get(`/blueprints?site_id=${siteId}`);
      setBlueprints(response.data.blueprints || []);
      if (response.data.blueprints && response.data.blueprints.length > 0) {
        setSelectedBlueprint(response.data.blueprints[0]);
      }
    } catch (err) {
      console.error('Failed to fetch blueprints:', err);
    }
  };

  const exportBlueprint = async (blueprintId: string, format: 'json' | 'yaml' = 'json') => {
    try {
      const response = await axios.get(`/blueprints/${blueprintId}/export?format=${format}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `blueprint_${site?.domain}_v${selectedBlueprint?.version}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to export blueprint: ' + (err as any).message);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error || !site) {
    return (
      <div className="container">
        <div className="card">
          <div className="alert alert-error">{error || 'Site not found'}</div>
          <button className="button" onClick={() => navigate('/sites')}>
            Back to Sites
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      {/* Header */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button className="button button-secondary" onClick={() => navigate('/sites')}>
          ← Back
        </button>
        <h1 style={{ margin: 0 }}>{site.domain}</h1>
        <span className={`badge badge-${site.status}`}>{site.status}</span>
      </div>

      {/* Tabs */}
      <div className="tabs" style={{ marginBottom: '1.5rem' }}>
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'fingerprint' ? 'active' : ''}`}
          onClick={() => setActiveTab('fingerprint')}
        >
          Fingerprint Data
        </button>
        <button
          className={`tab ${activeTab === 'blueprint' ? 'active' : ''}`}
          onClick={() => setActiveTab('blueprint')}
          disabled={blueprints.length === 0}
        >
          Blueprint {blueprints.length > 0 ? `(${blueprints.length})` : ''}
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="card">
          <div className="card-title">Site Overview</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Domain
              </label>
              <div style={{ fontFamily: 'monospace', fontSize: '1rem' }}>{site.domain}</div>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Platform
              </label>
              <div>{site.platform || 'Not detected'}</div>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Status
              </label>
              <span className={`badge badge-${site.status}`}>{site.status}</span>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Complexity Score
              </label>
              <div>{site.complexity_score ? `${(site.complexity_score * 100).toFixed(0)}%` : 'Not calculated'}</div>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Business Value Score
              </label>
              <div>{site.business_value_score ? `${(site.business_value_score * 100).toFixed(0)}%` : 'Not set'}</div>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Blueprint Version
              </label>
              <div>v{site.blueprint_version}</div>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Created
              </label>
              <div style={{ fontSize: '0.875rem' }}>{new Date(site.created_at).toLocaleString()}</div>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                Last Discovered
              </label>
              <div style={{ fontSize: '0.875rem' }}>
                {site.last_discovered_at ? new Date(site.last_discovered_at).toLocaleString() : 'Never'}
              </div>
            </div>
          </div>
          {site.notes && (
            <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
              <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.5rem' }}>
                Notes
              </label>
              <div>{site.notes}</div>
            </div>
          )}
        </div>
      )}

      {/* Fingerprint Tab */}
      {activeTab === 'fingerprint' && (
        <div className="card">
          <div className="card-title">Fingerprint Data</div>
          {site.fingerprint_data ? (
            <div>
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Technology Stack</h3>
                {site.fingerprint_data.technologies ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {Object.entries(site.fingerprint_data.technologies).map(([key, value]: [string, any]) => (
                      <span key={key} className="badge badge-info" style={{ fontSize: '0.875rem' }}>
                        {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div style={{ color: '#6b7280' }}>No technology data available</div>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Metadata</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                  {Object.entries(site.fingerprint_data)
                    .filter(([key]) => key !== 'technologies')
                    .map(([key, value]) => (
                      <div key={key}>
                        <label style={{ fontSize: '0.875rem', color: '#6b7280', display: 'block', marginBottom: '0.25rem' }}>
                          {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </label>
                        <div style={{ fontSize: '0.875rem' }}>
                          {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              <details style={{ marginTop: '1rem' }}>
                <summary style={{ cursor: 'pointer', fontWeight: 500, marginBottom: '0.5rem' }}>
                  Raw JSON Data
                </summary>
                <pre style={{
                  backgroundColor: '#1f2937',
                  color: '#e5e7eb',
                  padding: '1rem',
                  borderRadius: '0.5rem',
                  overflow: 'auto',
                  fontSize: '0.875rem'
                }}>
                  {JSON.stringify(site.fingerprint_data, null, 2)}
                </pre>
              </details>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
              No fingerprint data available. The site has not been fingerprinted yet.
            </div>
          )}
        </div>
      )}

      {/* Blueprint Tab */}
      {activeTab === 'blueprint' && (
        <div>
          {blueprints.length > 0 ? (
            <>
              {/* Blueprint Version Selector */}
              <div className="card" style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                  <label style={{ fontWeight: 500 }}>Select Version:</label>
                  <select
                    className="form-input"
                    style={{ flex: 1, minWidth: '200px' }}
                    value={selectedBlueprint?.blueprint_id || ''}
                    onChange={(e) => {
                      const bp = blueprints.find(b => b.blueprint_id === e.target.value);
                      setSelectedBlueprint(bp || null);
                    }}
                  >
                    {blueprints.map((bp) => (
                      <option key={bp.blueprint_id} value={bp.blueprint_id}>
                        v{bp.version} - {new Date(bp.created_at).toLocaleDateString()} 
                        {bp.confidence_score ? ` (Confidence: ${(bp.confidence_score * 100).toFixed(0)}%)` : ''}
                      </option>
                    ))}
                  </select>
                  <button
                    className="button"
                    onClick={() => selectedBlueprint && exportBlueprint(selectedBlueprint.blueprint_id, 'json')}
                    disabled={!selectedBlueprint}
                  >
                    📥 Export JSON
                  </button>
                  <button
                    className="button button-secondary"
                    onClick={() => selectedBlueprint && exportBlueprint(selectedBlueprint.blueprint_id, 'yaml')}
                    disabled={!selectedBlueprint}
                  >
                    📥 Export YAML
                  </button>
                </div>
              </div>

              {selectedBlueprint && (
                <>
                  {/* Categories */}
                  <div className="card" style={{ marginBottom: '1rem' }}>
                    <div className="card-title">Categories ({Array.isArray(selectedBlueprint.categories_data) ? selectedBlueprint.categories_data.length : 0})</div>
                    {Array.isArray(selectedBlueprint.categories_data) && selectedBlueprint.categories_data.length > 0 ? (
                      <div style={{ display: 'grid', gap: '0.75rem' }}>
                        {selectedBlueprint.categories_data.map((cat: any, idx: number) => (
                          <div key={idx} style={{ padding: '0.75rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
                            <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>{cat.name || cat.category_name || `Category ${idx + 1}`}</div>
                            {cat.url && <div style={{ fontSize: '0.875rem', color: '#6b7280', fontFamily: 'monospace' }}>{cat.url}</div>}
                            {cat.description && <div style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{cat.description}</div>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ color: '#6b7280' }}>No categories found</div>
                    )}
                  </div>

                  {/* Endpoints */}
                  <div className="card" style={{ marginBottom: '1rem' }}>
                    <div className="card-title">Endpoints ({Array.isArray(selectedBlueprint.endpoints_data) ? selectedBlueprint.endpoints_data.length : 0})</div>
                    {Array.isArray(selectedBlueprint.endpoints_data) && selectedBlueprint.endpoints_data.length > 0 ? (
                      <div style={{ display: 'grid', gap: '0.75rem' }}>
                        {selectedBlueprint.endpoints_data.map((endpoint: any, idx: number) => (
                          <div key={idx} style={{ padding: '0.75rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
                            <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>{endpoint.name || `Endpoint ${idx + 1}`}</div>
                            {endpoint.url && <div style={{ fontSize: '0.875rem', color: '#6b7280', fontFamily: 'monospace' }}>{endpoint.url}</div>}
                            {endpoint.method && <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>{endpoint.method}</span>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ color: '#6b7280' }}>No endpoints found</div>
                    )}
                  </div>

                  {/* Selectors */}
                  <div className="card" style={{ marginBottom: '1rem' }}>
                    <div className="card-title">Selectors ({Array.isArray(selectedBlueprint.selectors_data) ? selectedBlueprint.selectors_data.length : 0})</div>
                    {Array.isArray(selectedBlueprint.selectors_data) && selectedBlueprint.selectors_data.length > 0 ? (
                      <table className="table">
                        <thead>
                          <tr>
                            <th>Field</th>
                            <th>Selector</th>
                            <th>Method</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedBlueprint.selectors_data.map((sel: any, idx: number) => (
                            <tr key={idx}>
                              <td>{sel.field_name || sel.name || '-'}</td>
                              <td style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>{sel.selector || sel.css_selector || '-'}</td>
                              <td><span className="badge badge-info">{sel.method || sel.extraction_method || '-'}</span></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div style={{ color: '#6b7280' }}>No selectors found</div>
                    )}
                  </div>

                  {/* Render Hints */}
                  <div className="card">
                    <div className="card-title">Render Hints</div>
                    {selectedBlueprint.render_hints_data && Object.keys(selectedBlueprint.render_hints_data).length > 0 ? (
                      <pre style={{
                        backgroundColor: '#1f2937',
                        color: '#e5e7eb',
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        overflow: 'auto',
                        fontSize: '0.875rem'
                      }}>
                        {JSON.stringify(selectedBlueprint.render_hints_data, null, 2)}
                      </pre>
                    ) : (
                      <div style={{ color: '#6b7280' }}>No render hints available</div>
                    )}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="card">
              <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                No blueprints available for this site yet.
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SiteDetails;

