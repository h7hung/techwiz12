import { useState } from 'react'
import { Navigate, NavLink, Route, Routes } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import ClaimAnalysis from './pages/ClaimAnalysis'
import Claims from './pages/Claims'

function SettingsPlaceholder() {
  return (
    <section className="content-panel settings-placeholder">
      <p className="eyebrow">WORKSPACE</p>
      <h2>Settings</h2>
      <p>Settings will be available when the AssureX backend is connected.</p>
    </section>
  )
}

function App() {
  const [lastAnalysis, setLastAnalysis] = useState(null)

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-shell">
        <Header />
        <main className="page-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<ClaimAnalysis onAnalysis={setLastAnalysis} result={lastAnalysis} />} />
            <Route path="/claims" element={<Claims />} />
            <Route path="/settings" element={<SettingsPlaceholder />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
