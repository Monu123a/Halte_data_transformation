import { useState, useEffect } from 'react';
import './ConfigPanel.css';

const API = import.meta.env.VITE_API_URL || 'https://halte-data-transformation.onrender.com';

export default function ConfigPanel() {
  const [open, setOpen] = useState(false);
  const [rules, setRules] = useState(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetch(`${API}/api/config`)
      .then(r => r.json())
      .then(data => setRules(data.rules || {}))
      .catch(() => {});
  }, []);

  const updateRule = (plugin, key, value) => {
    setRules(prev => ({
      ...prev,
      [plugin]: { ...prev[plugin], [key]: value }
    }));
  };

  const save = async () => {
    setSaving(true);
    setMsg('');
    try {
      await fetch(`${API}/api/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rules }),
      });
      setMsg('✅ Saved');
      setTimeout(() => setMsg(''), 2000);
    } catch {
      setMsg('❌ Failed');
    }
    setSaving(false);
  };

  if (!rules) {
    return (
      <div className="card config-panel">
        <div className="card-title">⚙️ Configuration</div>
        <div style={{ padding: 15, fontSize: 13, color: '#94a3b8' }}>
          Connecting to backend server... (If server is waking up, please wait a few seconds)
        </div>
      </div>
    );
  }

  return (
    <div className="card config-panel">
      <div className="card-title" onClick={() => setOpen(!open)}>
        ⚙️ Configuration
        <span className={`config-toggle ${open ? 'open' : ''}`}>▼</span>
      </div>

      <div className={`config-body ${open ? 'open' : ''}`}>
        {/* Transaction Rules */}
        <div className="config-section">
          <div className="config-section-title">Transaction Rules</div>
          <div className="form-group">
            <label className="form-label">Allowed Transaction Types (comma-separated)</label>
            <input
              className="form-input"
              value={(rules.TransactionFilter?.allowed || []).join(', ')}
              onChange={e => updateRule('TransactionFilter', 'allowed',
                e.target.value.split(',').map(s => s.trim()).filter(Boolean)
              )}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Invoice Prefixes (comma-separated)</label>
            <input
              className="form-input"
              value={(rules.InvoiceFilter?.prefixes || []).join(', ')}
              onChange={e => updateRule('InvoiceFilter', 'prefixes',
                e.target.value.split(',').map(s => s.trim()).filter(Boolean)
              )}
            />
          </div>
        </div>

        {/* Location Rules */}
        <div className="config-section">
          <div className="config-section-title">Location Rules</div>
          <div className="form-group">
            <label className="form-label">Allowed States (comma-separated)</label>
            <input
              className="form-input"
              value={(rules.LocationFilter?.allowed_states || []).join(', ')}
              onChange={e => updateRule('LocationFilter', 'allowed_states',
                e.target.value.split(',').map(s => s.trim()).filter(Boolean)
              )}
            />
          </div>
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input
                type="checkbox"
                checked={rules.LocationFilter?.enabled || false}
                onChange={e => updateRule('LocationFilter', 'enabled', e.target.checked)}
              />
              Enable Location Filter
            </label>
          </div>
        </div>

        {/* SKU Rules */}
        <div className="config-section">
          <div className="config-section-title">SKU Rules</div>
          <div className="form-group">
            <label className="form-label">SKU Trim Length</label>
            <input
              type="number"
              className="form-input"
              value={rules.SkuTrim?.length || 6}
              onChange={e => updateRule('SkuTrim', 'length', parseInt(e.target.value) || 6)}
            />
          </div>
        </div>

        {/* Default Values */}
        <div className="config-section">
          <div className="config-section-title">Default Values</div>
          <div className="form-group">
            <label className="form-label">MEM SHIP</label>
            <input
              className="form-input"
              value={rules.DefaultInjector?.defaults?.['MEM SHIP'] || ''}
              onChange={e => updateRule('DefaultInjector', 'defaults',
                { ...rules.DefaultInjector?.defaults, 'MEM SHIP': e.target.value }
              )}
            />
          </div>
          <div className="form-group">
            <label className="form-label">TAX REGION</label>
            <input
              className="form-input"
              value={rules.DefaultInjector?.defaults?.['TAX REGION'] || ''}
              onChange={e => updateRule('DefaultInjector', 'defaults',
                { ...rules.DefaultInjector?.defaults, 'TAX REGION': e.target.value }
              )}
            />
          </div>
        </div>

        <div className="config-actions">
          <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? '⏳ Saving...' : '💾 Save Configuration'}
          </button>
          {msg && <span style={{ fontSize: 13, alignSelf: 'center' }}>{msg}</span>}
        </div>
      </div>
    </div>
  );
}
