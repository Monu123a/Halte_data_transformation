import './StatusPanel.css';

export default function StatusPanel({ stats, warnings, success }) {
  if (!stats && !success) return null;

  return (
    <div className="card">
      <div className="card-title">📊 Processing Report</div>

      {success && (
        <div className="success-banner">✅ Transformation Completed Successfully!</div>
      )}

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.rows_read}</div>
            <div className="stat-label">Rows Read</div>
          </div>
          <div className="stat-card">
            <div className="stat-value success">{stats.rows_processed}</div>
            <div className="stat-label">Rows Processed</div>
          </div>
          <div className="stat-card">
            <div className="stat-value warning">{stats.rows_removed}</div>
            <div className="stat-label">Rows Removed</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.execution_time_ms} ms</div>
            <div className="stat-label">Execution Time</div>
          </div>
          <div className="stat-card">
            <div className="stat-value error">{stats.duplicate_invoices}</div>
            <div className="stat-label">Duplicate Invoices</div>
          </div>
          <div className="stat-card">
            <div className="stat-value error">{stats.rows_failed}</div>
            <div className="stat-label">Rows Failed</div>
          </div>
        </div>
      )}

      {warnings && warnings.length > 0 && (
        <>
          <div className="card-title" style={{ marginTop: 8 }}>⚠️ Warnings ({warnings.length})</div>
          <div className="warnings-list">
            {warnings.map((w, i) => (
              <div key={i} className={`warning-item ${w.level}`}>
                <span className="warning-badge">{w.level}</span>
                <span>{w.message}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
