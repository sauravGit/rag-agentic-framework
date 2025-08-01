import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line, Bar } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import './Monitoring.css';

// Register Chart.js components
Chart.register(...registerables);

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function Monitoring() {
  const [metrics, setMetrics] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [timeRange, setTimeRange] = useState('1h');
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [metricSummary, setMetricSummary] = useState({});
  const [healthStatus, setHealthStatus] = useState({});

  useEffect(() => {
    // Initial data fetch
    fetchMonitoringData();
    
    // Set up interval for periodic refresh
    const intervalId = setInterval(fetchMonitoringData, refreshInterval * 1000);
    
    return () => {
      clearInterval(intervalId);
    };
  }, [timeRange, refreshInterval]);

  const fetchMonitoringData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Calculate time range in seconds
      let timeRangeSeconds = 3600; // Default 1h
      switch (timeRange) {
        case '15m': timeRangeSeconds = 900; break;
        case '1h': timeRangeSeconds = 3600; break;
        case '6h': timeRangeSeconds = 21600; break;
        case '24h': timeRangeSeconds = 86400; break;
        case '7d': timeRangeSeconds = 604800; break;
      }
      
      // Fetch metrics
      const metricsResponse = await axios.get(`${API_BASE_URL}/api/v1/monitoring/metrics`, {
        params: {
          start_time: Math.floor(Date.now() / 1000) - timeRangeSeconds
        }
      });
      
      // Fetch alerts
      const alertsResponse = await axios.get(`${API_BASE_URL}/api/v1/monitoring/alerts`);
      
      // Fetch metric summary
      const summaryResponse = await axios.get(`${API_BASE_URL}/api/v1/monitoring/metrics/summary`, {
        params: {
          window_seconds: timeRangeSeconds
        }
      });
      
      // Fetch health status
      const healthResponse = await axios.get(`${API_BASE_URL}/api/v1/health`);
      
      setMetrics(metricsResponse.data);
      setAlerts(alertsResponse.data);
      setMetricSummary(summaryResponse.data);
      setHealthStatus(healthResponse.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
      setError('Failed to fetch monitoring data. Please try again.');
      setIsLoading(false);
    }
  };

  const getChartData = (metricName) => {
    if (!metrics[metricName]) {
      return {
        labels: [],
        datasets: [{
          label: metricName,
          data: [],
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
        }]
      };
    }
    
    const data = metrics[metricName];
    
    return {
      labels: data.map(point => new Date(point.timestamp * 1000).toLocaleTimeString()),
      datasets: [{
        label: metricName,
        data: data.map(point => point.value),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4
      }]
    };
  };

  const renderOverviewTab = () => {
    return (
      <div className="monitoring-overview">
        <div className="health-status-cards">
          <div className={`health-card ${healthStatus.status || 'unknown'}`}>
            <h3>System Health</h3>
            <div className="health-status">{healthStatus.status || 'Unknown'}</div>
            <div className="health-message">{healthStatus.message || 'No health data available'}</div>
          </div>
          
          <div className="health-card alerts">
            <h3>Active Alerts</h3>
            <div className="alert-count">{alerts.filter(a => a.active).length}</div>
            <div className="alert-message">
              {alerts.filter(a => a.active).length > 0 
                ? 'Attention required' 
                : 'No active alerts'}
            </div>
          </div>
          
          <div className="health-card metrics">
            <h3>Metrics</h3>
            <div className="metric-count">{Object.keys(metrics).length}</div>
            <div className="metric-message">Metrics being monitored</div>
          </div>
        </div>
        
        <div className="key-metrics">
          <h3>Key Performance Metrics</h3>
          
          <div className="metrics-grid">
            {metricSummary['serving_request_duration'] && (
              <div className="metric-summary-card">
                <h4>Response Time</h4>
                <div className="metric-value">
                  {metricSummary['serving_request_duration'].avg.toFixed(2)}s
                </div>
                <div className="metric-range">
                  Min: {metricSummary['serving_request_duration'].min.toFixed(2)}s | 
                  Max: {metricSummary['serving_request_duration'].max.toFixed(2)}s
                </div>
              </div>
            )}
            
            {metricSummary['serving_request_count'] && (
              <div className="metric-summary-card">
                <h4>Request Volume</h4>
                <div className="metric-value">
                  {metricSummary['serving_request_count'].count} requests
                </div>
                <div className="metric-range">
                  Last: {metricSummary['serving_request_count'].latest.toFixed(0)}/min
                </div>
              </div>
            )}
            
            {metricSummary['evaluation_relevance_score'] && (
              <div className="metric-summary-card">
                <h4>Relevance Score</h4>
                <div className="metric-value">
                  {(metricSummary['evaluation_relevance_score'].avg * 100).toFixed(1)}%
                </div>
                <div className="metric-range">
                  Min: {(metricSummary['evaluation_relevance_score'].min * 100).toFixed(1)}% | 
                  Max: {(metricSummary['evaluation_relevance_score'].max * 100).toFixed(1)}%
                </div>
              </div>
            )}
            
            {metricSummary['serving_request_error'] && (
              <div className="metric-summary-card">
                <h4>Error Rate</h4>
                <div className="metric-value">
                  {(metricSummary['serving_request_error'].avg * 100).toFixed(2)}%
                </div>
                <div className="metric-range">
                  Min: {(metricSummary['serving_request_error'].min * 100).toFixed(2)}% | 
                  Max: {(metricSummary['serving_request_error'].max * 100).toFixed(2)}%
                </div>
              </div>
            )}
          </div>
        </div>
        
        <div className="recent-alerts">
          <h3>Recent Alerts</h3>
          {alerts.length > 0 ? (
            <table className="alerts-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Name</th>
                  <th>Severity</th>
                  <th>Description</th>
                  <th>Started</th>
                </tr>
              </thead>
              <tbody>
                {alerts.slice(0, 5).map((alert, index) => (
                  <tr key={index} className={alert.active ? 'active-alert' : 'resolved-alert'}>
                    <td>
                      <span className={`alert-status ${alert.active ? 'active' : 'resolved'}`}>
                        {alert.active ? 'Active' : 'Resolved'}
                      </span>
                    </td>
                    <td>{alert.name}</td>
                    <td className={`severity-${alert.severity}`}>{alert.severity}</td>
                    <td>{alert.description}</td>
                    <td>{new Date(alert.start_time * 1000).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="no-data">No alerts in the selected time range.</p>
          )}
        </div>
      </div>
    );
  };

  const renderMetricsTab = () => {
    return (
      <div className="monitoring-metrics">
        <div className="metrics-grid">
          {Object.keys(metrics).length > 0 ? (
            Object.keys(metrics).map(metricName => (
              <div key={metricName} className="metric-chart-card">
                <h3>{formatMetricName(metricName)}</h3>
                <div className="metric-chart">
                  <Line 
                    data={getChartData(metricName)} 
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: metricName.includes('score') || metricName.includes('rate')
                        }
                      }
                    }}
                  />
                </div>
                {metricSummary[metricName] && (
                  <div className="metric-summary">
                    <div>Avg: {metricSummary[metricName].avg.toFixed(2)}</div>
                    <div>Min: {metricSummary[metricName].min.toFixed(2)}</div>
                    <div>Max: {metricSummary[metricName].max.toFixed(2)}</div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="no-data">No metrics data available for the selected time range.</p>
          )}
        </div>
      </div>
    );
  };

  const renderAlertsTab = () => {
    return (
      <div className="monitoring-alerts">
        <div className="alerts-summary">
          <div className="alert-summary-card">
            <h3>Active Alerts</h3>
            <div className="alert-count">{alerts.filter(a => a.active).length}</div>
          </div>
          <div className="alert-summary-card">
            <h3>Resolved Alerts</h3>
            <div className="alert-count">{alerts.filter(a => !a.active).length}</div>
          </div>
          <div className="alert-summary-card">
            <h3>Critical Alerts</h3>
            <div className="alert-count">{alerts.filter(a => a.active && a.severity === 'critical').length}</div>
          </div>
          <div className="alert-summary-card">
            <h3>Warning Alerts</h3>
            <div className="alert-count">{alerts.filter(a => a.active && a.severity === 'warning').length}</div>
          </div>
        </div>
        
        <div className="alerts-list">
          <h3>All Alerts</h3>
          {alerts.length > 0 ? (
            <table className="alerts-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Name</th>
                  <th>Severity</th>
                  <th>Metric</th>
                  <th>Value</th>
                  <th>Description</th>
                  <th>Started</th>
                  <th>Last Updated</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert, index) => (
                  <tr key={index} className={alert.active ? 'active-alert' : 'resolved-alert'}>
                    <td>
                      <span className={`alert-status ${alert.active ? 'active' : 'resolved'}`}>
                        {alert.active ? 'Active' : 'Resolved'}
                      </span>
                    </td>
                    <td>{alert.name}</td>
                    <td className={`severity-${alert.severity}`}>{alert.severity}</td>
                    <td>{alert.metric_name}</td>
                    <td>{alert.value.toFixed(2)}</td>
                    <td>{alert.description}</td>
                    <td>{new Date(alert.start_time * 1000).toLocaleString()}</td>
                    <td>{new Date(alert.last_updated * 1000).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="no-data">No alerts in the selected time range.</p>
          )}
        </div>
      </div>
    );
  };

  const formatMetricName = (name) => {
    return name
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="monitoring-dashboard">
      <div className="monitoring-header">
        <h2>Monitoring Dashboard</h2>
        <div className="monitoring-controls">
          <div className="time-range-selector">
            <label>Time Range:</label>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <option value="15m">Last 15 minutes</option>
              <option value="1h">Last 1 hour</option>
              <option value="6h">Last 6 hours</option>
              <option value="24h">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
            </select>
          </div>
          
          <div className="refresh-interval-selector">
            <label>Refresh:</label>
            <select 
              value={refreshInterval} 
              onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
            >
              <option value="10">10 seconds</option>
              <option value="30">30 seconds</option>
              <option value="60">1 minute</option>
              <option value="300">5 minutes</option>
            </select>
          </div>
          
          <button 
            className="refresh-button" 
            onClick={fetchMonitoringData}
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>
      
      <div className="monitoring-tabs">
        <div 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </div>
        <div 
          className={`tab ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Metrics
        </div>
        <div 
          className={`tab ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          Alerts
        </div>
      </div>
      
      <div className="monitoring-content">
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <div>Loading monitoring data...</div>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'metrics' && renderMetricsTab()}
        {activeTab === 'alerts' && renderAlertsTab()}
      </div>
    </div>
  );
}

export default Monitoring;
