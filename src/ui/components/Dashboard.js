import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function Dashboard({ user, systemHealth }) {
  const [stats, setStats] = useState({
    totalQueries: 0,
    totalDocuments: 0,
    avgResponseTime: 0,
    avgRelevanceScore: 0,
    recentSessions: []
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Calculate time range in seconds
      let timeRangeSeconds = 86400; // Default 24h
      switch (timeRange) {
        case '1h': timeRangeSeconds = 3600; break;
        case '24h': timeRangeSeconds = 86400; break;
        case '7d': timeRangeSeconds = 604800; break;
        case '30d': timeRangeSeconds = 2592000; break;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v1/dashboard/stats`, {
        params: {
          time_range: timeRangeSeconds,
          user_id: user.role === 'admin' ? undefined : user.id
        }
      });
      
      setStats(response.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to fetch dashboard data. Please try again.');
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getHealthStatusClass = (status) => {
    switch (status) {
      case 'healthy': return 'status-healthy';
      case 'warning': return 'status-warning';
      case 'unhealthy': return 'status-unhealthy';
      default: return 'status-unknown';
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <div className="dashboard-controls">
          <div className="time-range-selector">
            <label>Time Range:</label>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <option value="1h">Last 1 hour</option>
              <option value="24h">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
            </select>
          </div>
          
          <button 
            className="refresh-button" 
            onClick={fetchDashboardData}
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>
      
      <div className="dashboard-content">
        {isLoading ? (
          <div className="loading-message">Loading dashboard data...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : (
          <>
            <div className="stats-cards">
              <div className="stat-card">
                <div className="stat-icon">🔍</div>
                <div className="stat-content">
                  <div className="stat-value">{stats.totalQueries}</div>
                  <div className="stat-label">Total Queries</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">📄</div>
                <div className="stat-content">
                  <div className="stat-value">{stats.totalDocuments}</div>
                  <div className="stat-label">Total Documents</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">⏱️</div>
                <div className="stat-content">
                  <div className="stat-value">{stats.avgResponseTime.toFixed(2)}s</div>
                  <div className="stat-label">Avg Response Time</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-content">
                  <div className="stat-value">{(stats.avgRelevanceScore * 100).toFixed(1)}%</div>
                  <div className="stat-label">Avg Relevance Score</div>
                </div>
              </div>
            </div>
            
            <div className="dashboard-sections">
              <div className="dashboard-section">
                <h3>Recent Sessions</h3>
                {stats.recentSessions.length > 0 ? (
                  <table className="sessions-table">
                    <thead>
                      <tr>
                        <th>Session ID</th>
                        <th>User</th>
                        <th>Started</th>
                        <th>Queries</th>
                        <th>Avg Response Time</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.recentSessions.map((session, index) => (
                        <tr key={index}>
                          <td>{session.session_id}</td>
                          <td>{session.user_name}</td>
                          <td>{formatDate(session.start_time)}</td>
                          <td>{session.query_count}</td>
                          <td>{session.avg_response_time.toFixed(2)}s</td>
                          <td className={`session-status status-${session.status}`}>
                            {session.status}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="no-data">No recent sessions found.</p>
                )}
              </div>
              
              <div className="dashboard-section">
                <h3>System Health</h3>
                {systemHealth && Object.keys(systemHealth).length > 0 ? (
                  <div className="health-status">
                    <div className={`overall-health ${getHealthStatusClass(systemHealth.status)}`}>
                      <h4>Overall Status</h4>
                      <div className="status-indicator">{systemHealth.status || 'Unknown'}</div>
                      {systemHealth.message && (
                        <div className="status-message">{systemHealth.message}</div>
                      )}
                    </div>
                    
                    {systemHealth.components && (
                      <div className="component-health">
                        <h4>Component Status</h4>
                        <table className="health-table">
                          <thead>
                            <tr>
                              <th>Component</th>
                              <th>Status</th>
                              <th>Details</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(systemHealth.components).map(([name, data], index) => (
                              <tr key={index}>
                                <td>{name}</td>
                                <td className={getHealthStatusClass(data.status)}>
                                  {data.status}
                                </td>
                                <td>{data.message || '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="no-data">No health data available.</p>
                )}
              </div>
            </div>
            
            <div className="dashboard-sections">
              <div className="dashboard-section">
                <h3>Popular Queries</h3>
                {stats.popularQueries && stats.popularQueries.length > 0 ? (
                  <table className="queries-table">
                    <thead>
                      <tr>
                        <th>Query</th>
                        <th>Count</th>
                        <th>Avg Response Time</th>
                        <th>Avg Relevance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.popularQueries.map((query, index) => (
                        <tr key={index}>
                          <td>{query.text}</td>
                          <td>{query.count}</td>
                          <td>{query.avg_response_time.toFixed(2)}s</td>
                          <td>{(query.avg_relevance * 100).toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="no-data">No query data available.</p>
                )}
              </div>
              
              <div className="dashboard-section">
                <h3>Recent Activity</h3>
                {stats.recentActivity && stats.recentActivity.length > 0 ? (
                  <div className="activity-list">
                    {stats.recentActivity.map((activity, index) => (
                      <div key={index} className="activity-item">
                        <div className="activity-time">
                          {formatDate(activity.timestamp)}
                        </div>
                        <div className="activity-icon">
                          {activity.type === 'query' ? '🔍' : 
                           activity.type === 'document' ? '📄' : 
                           activity.type === 'session' ? '👤' : '🔔'}
                        </div>
                        <div className="activity-content">
                          <div className="activity-title">{activity.title}</div>
                          <div className="activity-description">{activity.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-data">No recent activity found.</p>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
