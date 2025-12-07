import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

function AgentDetails({ token }) {
  const { agentId } = useParams()
  const navigate = useNavigate()

  const { data: agent, isLoading: agentLoading } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: async () => {
      const response = await axios.get(`/api/agents/${agentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    }
  })

  const { data: reports, isLoading: reportsLoading } = useQuery({
    queryKey: ['reports', agentId],
    queryFn: async () => {
      const response = await axios.get(`/api/reports?agent_id=${agentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    }
  })

  const triggerScan = async () => {
    try {
      await axios.post(`/api/agents/${agentId}/scan`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      alert('Scan triggered successfully!')
    } catch (err) {
      alert('Failed to trigger scan: ' + err.message)
    }
  }

  if (agentLoading) return <div className="loading">Loading agent details...</div>

  return (
    <div className="agent-details">
      <div className="page-header">
        <button onClick={() => navigate('/agents')} className="back-btn">
          ← Back to Agents
        </button>
        <h2>{agent.hostname}</h2>
        <button onClick={triggerScan} className="primary">
          Run Scan
        </button>
      </div>

      <div className="info-card">
        <h3>Agent Information</h3>
        <div className="info-grid">
          <div>
            <label>Hostname:</label>
            <span>{agent.hostname}</span>
          </div>
          <div>
            <label>OS:</label>
            <span>{agent.os} {agent.os_version}</span>
          </div>
          <div>
            <label>IP Address:</label>
            <span>{agent.ip || 'N/A'}</span>
          </div>
          <div>
            <label>Status:</label>
            <span className={`status ${agent.status}`}>{agent.status}</span>
          </div>
          <div>
            <label>Last Seen:</label>
            <span>{new Date(agent.last_seen).toLocaleString()}</span>
          </div>
          <div>
            <label>Registered:</label>
            <span>{new Date(agent.registered_at).toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className="reports-section">
        <h3>Recent Reports</h3>
        {reportsLoading ? (
          <div className="loading">Loading reports...</div>
        ) : reports.reports.length === 0 ? (
          <div className="empty-state">No reports yet</div>
        ) : (
          <table className="reports-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Mode</th>
                <th>Status</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {reports.reports.map(report => (
                <tr key={report.id}>
                  <td>{new Date(report.timestamp).toLocaleString()}</td>
                  <td>{report.mode || 'standard'}</td>
                  <td>
                    <span className={`status ${report.overall_status}`}>
                      {report.overall_status}
                    </span>
                  </td>
                  <td>{(report.overall_score * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default AgentDetails
