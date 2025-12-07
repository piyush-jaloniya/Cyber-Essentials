import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import axios from 'axios'

function AgentsList({ token }) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await axios.get('/api/agents', {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    }
  })

  const triggerBulkScan = async () => {
    try {
      await axios.post('/api/agents/scan', {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      alert('Bulk scan triggered successfully!')
    } catch (err) {
      alert('Failed to trigger scan: ' + err.message)
    }
  }

  if (isLoading) return <div className="loading">Loading agents...</div>
  if (error) return <div className="error">Error: {error.message}</div>

  return (
    <div className="agents-list">
      <div className="page-header">
        <h2>Registered Agents ({data.total})</h2>
        <div className="actions">
          <button onClick={refetch}>Refresh</button>
          <button onClick={triggerBulkScan} className="primary">
            Scan All Agents
          </button>
        </div>
      </div>

      {data.agents.length === 0 ? (
        <div className="empty-state">
          <p>No agents registered yet.</p>
          <p>Install and register agents on your endpoints to get started.</p>
        </div>
      ) : (
        <table className="agents-table">
          <thead>
            <tr>
              <th>Hostname</th>
              <th>OS</th>
              <th>IP</th>
              <th>Status</th>
              <th>Last Seen</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.agents.map(agent => (
              <tr key={agent.id}>
                <td>
                  <Link to={`/agents/${agent.id}`}>{agent.hostname}</Link>
                </td>
                <td>{agent.os} {agent.os_version}</td>
                <td>{agent.ip || 'N/A'}</td>
                <td>
                  <span className={`status ${agent.status}`}>
                    {agent.status}
                  </span>
                </td>
                <td>{new Date(agent.last_seen).toLocaleString()}</td>
                <td>
                  <Link to={`/agents/${agent.id}`} className="btn-small">
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default AgentsList
