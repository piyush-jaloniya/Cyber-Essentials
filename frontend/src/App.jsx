import React, { useState } from 'react'
import { Routes, Route, Link, Navigate } from 'react-router-dom'
import Login from './components/Login'
import AgentsList from './components/AgentsList'
import AgentDetails from './components/AgentDetails'
import ReportsList from './components/ReportsList'
import './App.css'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  if (!token) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>🛡️ CE Dashboard</h1>
        </div>
        <div className="navbar-menu">
          <Link to="/agents">Agents</Link>
          <Link to="/reports">Reports</Link>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/agents" />} />
          <Route path="/agents" element={<AgentsList token={token} />} />
          <Route path="/agents/:agentId" element={<AgentDetails token={token} />} />
          <Route path="/reports" element={<ReportsList token={token} />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
