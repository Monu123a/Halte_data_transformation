import './PreviewPanel.css';

export default function PreviewPanel({ columns, data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="card">
      <div className="card-title">👁 Transformation Preview</div>
      <p className="preview-info">Showing first {data.length} rows of {columns.length} columns</p>
      <div className="preview-table-wrapper">
        <table className="preview-table">
          <thead>
            <tr>
              <th className="row-num">#</th>
              {columns.map((col, i) => (
                <th key={i}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, ri) => (
              <tr key={ri}>
                <td className="row-num">{ri + 1}</td>
                {row.map((cell, ci) => (
                  <td key={ci} title={cell}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
