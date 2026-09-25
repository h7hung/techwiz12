import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard', icon: '▦' },
  { to: '/analyze', label: 'Analyze Claim', icon: '＋' },
  { to: '/claims', label: 'Claims', icon: '≡' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
]

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-mark">A</div>
        <div>
          <strong>AssureX</strong>
          <span>Claim Engine</span>
        </div>
      </div>

      <nav className="main-nav" aria-label="Primary navigation">
        <p className="nav-label">Workspace</p>
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon" aria-hidden="true">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-foot">
        <div className="status-dot" />
        <div>
          <strong>Workspace ready</strong>
          <span>SQLite claim records</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
