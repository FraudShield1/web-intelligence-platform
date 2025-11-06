import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Template {
  template_id: string;
  platform_name: string;
  platform_variant: string | null;
  category_selectors: any;
  product_list_selectors: any;
  api_patterns: any;
  render_hints: any;
  confidence: number | null;
  active: boolean;
  match_patterns: any;
  created_at: string;
  updated_at: string;
}

const Templates = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState({ platform: '', active: '' });
  const [total, setTotal] = useState(0);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, [filter]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter.platform) params.append('platform_name', filter.platform);
      if (filter.active !== '') params.append('active', filter.active);
      
      const response = await axios.get(`/templates?${params}`);
      setTemplates(response.data.templates || []);
      setTotal(response.data.total || 0);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteTemplate = async (templateId: string) => {
    if (!window.confirm('Are you sure you want to delete this template?')) return;
    try {
      await axios.delete(`/templates/${templateId}`);
      fetchTemplates();
    } catch (err: any) {
      alert('Failed to delete template: ' + (err.response?.data?.detail || err.message));
    }
  };

  const toggleActive = async (template: Template) => {
    try {
      await axios.put(`/templates/${template.template_id}`, {
        active: !template.active
      });
      fetchTemplates();
    } catch (err: any) {
      alert('Failed to update template: ' + (err.response?.data?.detail || err.message));
    }
  };

  const viewTemplate = (template: Template) => {
    setEditingTemplate(template);
    setShowCreateModal(true);
  };

  return (
    <div className="page-body">
      <div className="page-header" style={{ background: 'transparent', border: 'none', paddingBottom: 0 }}>
        <h1 className="page-title">Platform Templates</h1>
        <button
          className="button button-primary"
          onClick={() => {
            setEditingTemplate(null);
            setShowCreateModal(true);
          }}
        >
          + Create Template
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-title">Filters</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Platform</label>
            <select
              className="form-input"
              value={filter.platform}
              onChange={(e) => setFilter({ ...filter, platform: e.target.value })}
            >
              <option value="">All Platforms</option>
              <option value="shopify">Shopify</option>
              <option value="magento">Magento</option>
              <option value="woocommerce">WooCommerce</option>
              <option value="bigcommerce">BigCommerce</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Status</label>
            <select
              className="form-input"
              value={filter.active}
              onChange={(e) => setFilter({ ...filter, active: e.target.value })}
            >
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Total Templates</label>
            <div style={{ padding: '0.5rem', fontSize: '1.25rem', fontWeight: 'bold' }}>
              {total}
            </div>
          </div>
        </div>
      </div>

      {/* Templates Table */}
      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading templates...</p>
        </div>
      ) : templates.length > 0 ? (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Platform</th>
                <th>Variant</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Selectors</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {templates.map((template) => (
                <tr key={template.template_id}>
                  <td>
                    <strong>{template.platform_name}</strong>
                  </td>
                  <td>{template.platform_variant || '-'}</td>
                  <td>
                    {template.confidence
                      ? (template.confidence * 100).toFixed(0) + '%'
                      : '-'}
                  </td>
                  <td>
                    <span
                      className={`badge ${template.active ? 'badge-success' : 'badge-warning'}`}
                    >
                      {template.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    {template.product_list_selectors
                      ? Object.keys(template.product_list_selectors).length + ' selectors'
                      : '0 selectors'}
                  </td>
                  <td style={{ fontSize: '0.875rem' }}>
                    {new Date(template.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <button
                        className="button"
                        onClick={() => viewTemplate(template)}
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                      >
                        View
                      </button>
                      <button
                        className="button"
                        onClick={() => toggleActive(template)}
                        style={{
                          fontSize: '0.75rem',
                          padding: '0.25rem 0.5rem',
                          backgroundColor: template.active ? '#f59e0b' : '#10b981',
                          borderColor: template.active ? '#f59e0b' : '#10b981'
                        }}
                      >
                        {template.active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        className="button button-danger"
                        onClick={() => deleteTemplate(template.template_id)}
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
          No templates found. Create one to get started!
        </div>
      )}

      {/* Create/Edit Modal */}
      {showCreateModal && (
        <TemplateModal
          template={editingTemplate}
          onClose={() => {
            setShowCreateModal(false);
            setEditingTemplate(null);
          }}
          onSave={() => {
            setShowCreateModal(false);
            setEditingTemplate(null);
            fetchTemplates();
          }}
        />
      )}
    </div>
  );
};

// Template Modal Component
const TemplateModal = ({ template, onClose, onSave }: {
  template: Template | null;
  onClose: () => void;
  onSave: () => void;
}) => {
  const [formData, setFormData] = useState({
    platform_name: template?.platform_name || '',
    platform_variant: template?.platform_variant || '',
    confidence: template?.confidence || 0.9,
    active: template?.active ?? true,
    category_selectors: JSON.stringify(template?.category_selectors || {}, null, 2),
    product_list_selectors: JSON.stringify(template?.product_list_selectors || {}, null, 2),
    api_patterns: JSON.stringify(template?.api_patterns || {}, null, 2),
    render_hints: JSON.stringify(template?.render_hints || {}, null, 2),
    match_patterns: JSON.stringify(template?.match_patterns || {}, null, 2)
  });

  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Parse JSON fields
      const payload = {
        platform_name: formData.platform_name,
        platform_variant: formData.platform_variant || null,
        confidence: formData.confidence,
        active: formData.active,
        category_selectors: JSON.parse(formData.category_selectors),
        product_list_selectors: JSON.parse(formData.product_list_selectors),
        api_patterns: JSON.parse(formData.api_patterns),
        render_hints: JSON.parse(formData.render_hints),
        match_patterns: JSON.parse(formData.match_patterns)
      };

      if (template) {
        await axios.put(`/templates/${template.template_id}`, payload);
      } else {
        await axios.post('/templates', payload);
      }
      
      onSave();
    } catch (err: any) {
      alert('Failed to save template: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          maxWidth: '800px',
          maxHeight: '90vh',
          overflow: 'auto',
          width: '100%',
          margin: '1rem'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="card-title">
          {template ? 'Edit Template' : 'Create Template'}
          <button
            onClick={onClose}
            style={{
              float: 'right',
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>

        <div style={{ display: 'grid', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Platform Name *</label>
            <input
              type="text"
              className="form-input"
              value={formData.platform_name}
              onChange={(e) => setFormData({ ...formData, platform_name: e.target.value })}
              placeholder="e.g., shopify, magento"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Platform Variant</label>
            <input
              type="text"
              className="form-input"
              value={formData.platform_variant}
              onChange={(e) => setFormData({ ...formData, platform_variant: e.target.value })}
              placeholder="e.g., 2.x, 1.x"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Confidence (0-1)</label>
              <input
                type="number"
                className="form-input"
                value={formData.confidence}
                onChange={(e) => setFormData({ ...formData, confidence: parseFloat(e.target.value) })}
                min="0"
                max="1"
                step="0.01"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Active</label>
              <select
                className="form-input"
                value={formData.active.toString()}
                onChange={(e) => setFormData({ ...formData, active: e.target.value === 'true' })}
              >
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Category Selectors (JSON)</label>
            <textarea
              className="form-input"
              value={formData.category_selectors}
              onChange={(e) => setFormData({ ...formData, category_selectors: e.target.value })}
              rows={4}
              style={{ fontFamily: 'monospace' }}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Product List Selectors (JSON)</label>
            <textarea
              className="form-input"
              value={formData.product_list_selectors}
              onChange={(e) => setFormData({ ...formData, product_list_selectors: e.target.value })}
              rows={4}
              style={{ fontFamily: 'monospace' }}
            />
          </div>

          <div className="form-group">
            <label className="form-label">API Patterns (JSON)</label>
            <textarea
              className="form-input"
              value={formData.api_patterns}
              onChange={(e) => setFormData({ ...formData, api_patterns: e.target.value })}
              rows={3}
              style={{ fontFamily: 'monospace' }}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Render Hints (JSON)</label>
            <textarea
              className="form-input"
              value={formData.render_hints}
              onChange={(e) => setFormData({ ...formData, render_hints: e.target.value })}
              rows={3}
              style={{ fontFamily: 'monospace' }}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Match Patterns (JSON)</label>
            <textarea
              className="form-input"
              value={formData.match_patterns}
              onChange={(e) => setFormData({ ...formData, match_patterns: e.target.value })}
              rows={3}
              style={{ fontFamily: 'monospace' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
            <button className="button" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button
              className="button button-primary"
              onClick={handleSave}
              disabled={saving || !formData.platform_name}
            >
              {saving ? 'Saving...' : template ? 'Update' : 'Create'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Templates;

