import React from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

function ReportsList({ token }) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['all-reports'],
    queryFn: async () => {
      const response = await axios.get('/api/reports?limit=50', {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    }
  })

  if (isLoading) return <div className="loading">Loading reports...</div>
  if (error) return <div className="error">Error: {error.message}</div>

  return (
    <div className="reports-list">
      <div className="page-header">
        <h2>All Reports ({data.total})</h2>
        <button onClick={refetch}>Refresh</button>
      </div>

      {data.reports.length === 0 ? (
        <div className="empty-state">
          <p>No reports yet.</p>
        </div>
      ) : (
        <table className="reports-table">
          <thead>
            <tr>
              <th>Agent ID</th>
              <th>Timestamp</th>
              <th>Mode</th>
              <th>Status</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {data.reports.map(report => (
              <tr key={report.id}>
                <td>{report.agent_id.substring(0, 8)}...</td>
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
  )
}

export default ReportsList
