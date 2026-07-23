import './Header.css';

export default function Header() {
  return (
    <header className="header">
      <h1 className="header-title">Amazon Logic Transformer</h1>
      <p className="header-subtitle">
        Transform Amazon Seller Central Reports → Logic ERP Compatible Excel
      </p>
      <span className="header-badge">v1.0.0</span>
    </header>
  );
}
