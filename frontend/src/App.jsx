import { useState } from 'react';
import './App.css';
import Header from './components/Header';
import UploadPanel from './components/UploadPanel';
import ConfigPanel from './components/ConfigPanel';
import StatusPanel from './components/StatusPanel';
import PreviewPanel from './components/PreviewPanel';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [stats, setStats] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [previewCols, setPreviewCols] = useState([]);
  const [previewData, setPreviewData] = useState([]);
  const [outputFile, setOutputFile] = useState('');
  const [auditFile, setAuditFile] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const filenames = uploadedFiles.map(f => f.name);

  const handleTransform = async () => {
    if (!filenames.length) return;
    setLoading(true);
    setSuccess(false);
    setPreviewData([]);
    setPreviewCols([]);
    try {
      const res = await fetch(`${API}/api/transform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filenames }),
      });
      const data = await res.json();
      setStats(data.stats);
      setWarnings(data.warnings || []);
      setOutputFile(data.output_filename || '');
      setAuditFile(data.audit_filename || '');
      setSuccess(true);
    } catch (err) {
      setWarnings([{ level: 'CRITICAL', message: 'Transform request failed: ' + err.message }]);
    }
    setLoading(false);
  };

  const handleDryRun = async () => {
    if (!filenames.length) return;
    setLoading(true);
    setSuccess(false);
    try {
      const res = await fetch(`${API}/api/dry-run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filenames }),
      });
      const data = await res.json();
      setStats(data.stats);
      setWarnings(data.warnings || []);
      setPreviewCols(data.preview_columns || []);
      setPreviewData(data.preview_data || []);
      setOutputFile('');
    } catch (err) {
      setWarnings([{ level: 'CRITICAL', message: 'Dry run failed: ' + err.message }]);
    }
    setLoading(false);
  };

  const handleDownload = () => {
    if (!outputFile) return;
    const a = document.createElement('a');
    a.href = `${API}/api/download/${outputFile}`;
    a.download = outputFile;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleDownloadAudit = () => {
    if (!auditFile) return;
    const a = document.createElement('a');
    a.href = `${API}/api/download/${auditFile}`;
    a.download = auditFile;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleReset = async () => {
    try { await fetch(`${API}/api/reset`, { method: 'DELETE' }); } catch {}
    setUploadedFiles([]);
    setStats(null);
    setWarnings([]);
    setPreviewCols([]);
    setPreviewData([]);
    setOutputFile('');
    setAuditFile('');
    setSuccess(false);
  };

  return (
    <div className="app-container">
      <Header />

      {loading && (
        <div className="progress-bar-container">
          <div className="progress-bar-fill" style={{ width: '100%' }} />
        </div>
      )}

      <div className="action-bar" style={{ marginTop: 20 }}>
        <button
          className="btn btn-primary"
          onClick={handleTransform}
          disabled={!filenames.length || loading}
        >
          🔄 Transform Data
        </button>
        <button
          className="btn"
          onClick={handleDryRun}
          disabled={!filenames.length || loading}
        >
          👁 Dry Run Preview
        </button>
        <button
          className="btn btn-success"
          onClick={handleDownload}
          disabled={!outputFile}
        >
          📥 Download Output
        </button>
        {auditFile && (
          <button
            className="btn btn-warning"
            onClick={handleDownloadAudit}
          >
            📋 Download Audit Report
          </button>
        )}
        <button className="btn btn-danger" onClick={handleReset}>
          🗑 Reset
        </button>
      </div>

      <div className="main-grid">
        <div className="left-column">
          <UploadPanel uploadedFiles={uploadedFiles} setUploadedFiles={setUploadedFiles} />
          <PreviewPanel columns={previewCols} data={previewData} />
        </div>
        <div className="right-column">
          <ConfigPanel />
          <StatusPanel stats={stats} warnings={warnings} success={success} />
        </div>
      </div>
    </div>
  );
}
