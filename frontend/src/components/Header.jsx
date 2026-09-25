import { useLocation } from 'react-router-dom'

const titles = {
  '/': ['Dashboard', 'Warranty claim overview'],
  '/analyze': ['Analyze a claim', 'Enter claim information and receive a clear recommendation.'],
  '/claims': ['Claims', 'Review claims stored in the current workspace.'],
}

function Header() {
  const location = useLocation()
  const [title, subtitle] = titles[location.pathname] || titles['/']

  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">ASSUREX CLAIM OPERATIONS</p>
        <h1>{title}</h1>
        <p className="topbar-subtitle">{subtitle}</p>
      </div>
      <div className="user-chip">
        <span className="avatar">AM</span>
        <span><strong>Alex Morgan</strong><small>Claims analyst</small></span>
      </div>
    </header>
  )
}

export default Header
