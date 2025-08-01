import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Governance.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function Governance() {
  const [auditLogs, setAuditLogs] = useState([]);
  const [accessPolicies, setAccessPolicies] = useState([]);
  const [complianceStatus, setComplianceStatus] = useState({});
  const [timeRange, setTimeRange] = useState('24h');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('audit');
  const [filterOptions, setFilterOptions] = useState({
    eventType: '',
    resourceType: '',
    userId: '',
    status: ''
  });
  const [policyFormVisible, setPolicyFormVisible] = useState(false);
  const [newPolicy, setNewPolicy] = useState({
    name: '',
    description: '',
    resource_type: '',
    actions: [],
    conditions: {},
    priority: 0
  });

  useEffect(() => {
    // Initial data fetch
    fetchGovernanceData();
  }, [timeRange]);

  const fetchGovernanceData = async () => {
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
      
      const startTime = Math.floor(Date.now() / 1000) - timeRangeSeconds;
      
      // Fetch audit logs
      const auditResponse = await axios.get(`${API_BASE_URL}/api/v1/governance/audit-logs`, {
        params: {
          start_time: startTime,
          limit: 1000,
          event_type: filterOptions.eventType || undefined,
          resource_type: filterOptions.resourceType || undefined,
          user_id: filterOptions.userId || undefined,
          status: filterOptions.status || undefined
        }
      });
      
      // Fetch access policies
      const policiesResponse = await axios.get(`${API_BASE_URL}/api/v1/governance/access-policies`);
      
      // Fetch compliance status
      const complianceResponse = await axios.get(`${API_BASE_URL}/api/v1/governance/compliance-status`);
      
      setAuditLogs(auditResponse.data);
      setAccessPolicies(policiesResponse.data);
      setComplianceStatus(complianceResponse.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching governance data:', error);
      setError('Failed to fetch governance data. Please try again.');
      setIsLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilterOptions({
      ...filterOptions,
      [field]: value
    });
  };

  const applyFilters = () => {
    fetchGovernanceData();
  };

  const resetFilters = () => {
    setFilterOptions({
      eventType: '',
      resourceType: '',
      userId: '',
      status: ''
    });
    fetchGovernanceData();
  };

  const handlePolicyChange = (field, value) => {
    setNewPolicy({
      ...newPolicy,
      [field]: value
    });
  };

  const handleActionsChange = (e) => {
    const actions = e.target.value.split(',').map(action => action.trim());
    setNewPolicy({
      ...newPolicy,
      actions
    });
  };

  const handleConditionsChange = (e) => {
    try {
      const conditions = JSON.parse(e.target.value);
      setNewPolicy({
        ...newPolicy,
        conditions
      });
    } catch (error) {
      // Invalid JSON, but don't show error until submit
      console.log('Invalid JSON for conditions');
    }
  };

  const submitNewPolicy = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/v1/governance/access-policies`, newPolicy);
      setPolicyFormVisible(false);
      setNewPolicy({
        name: '',
        description: '',
        resource_type: '',
        actions: [],
        conditions: {},
        priority: 0
      });
      fetchGovernanceData();
    } catch (error) {
      console.error('Error creating policy:', error);
      setError('Failed to create policy. Please check your inputs and try again.');
    }
  };

  const renderAuditTab = () => {
    return (
      <div className="governance-audit">
        <div className="audit-filters">
          <h3>Filter Audit Logs</h3>
          <div className="filter-controls">
            <div className="filter-group">
              <label>Event Type:</label>
              <input 
                type="text" 
                value={filterOptions.eventType}
                onChange={(e) => handleFilterChange('eventType', e.target.value)}
                placeholder="e.g., access_decision"
              />
            </div>
            
            <div className="filter-group">
              <label>Resource Type:</label>
              <input 
                type="text" 
                value={filterOptions.resourceType}
                onChange={(e) => handleFilterChange('resourceType', e.target.value)}
                placeholder="e.g., medical_data"
              />
            </div>
            
            <div className="filter-group">
              <label>User ID:</label>
              <input 
                type="text" 
                value={filterOptions.userId}
                onChange={(e) => handleFilterChange('userId', e.target.value)}
                placeholder="e.g., user123"
              />
            </div>
            
            <div className="filter-group">
              <label>Status:</label>
              <select
                value={filterOptions.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <option value="">All</option>
                <option value="allowed">Allowed</option>
                <option value="denied">Denied</option>
                <option value="error">Error</option>
              </select>
            </div>
            
            <div className="filter-actions">
              <button onClick={applyFilters}>Apply Filters</button>
              <button onClick={resetFilters}>Reset</button>
            </div>
          </div>
        </div>
        
        <div className="audit-logs">
          <h3>Audit Logs</h3>
          {auditLogs.length > 0 ? (
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Event Type</th>
                  <th>User ID</th>
                  <th>Resource Type</th>
                  <th>Action</th>
                  <th>Status</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log, index) => (
                  <tr key={index} className={`status-${log.status.toLowerCase()}`}>
                    <td>{new Date(log.timestamp * 1000).toLocaleString()}</td>
                    <td>{log.event_type}</td>
                    <td>{log.user_id || '-'}</td>
                    <td>{log.resource_type}</td>
                    <td>{log.action}</td>
                    <td className={`status-${log.status.toLowerCase()}`}>{log.status}</td>
                    <td>
                      <button 
                        className="details-button"
                        onClick={() => alert(JSON.stringify(log.details, null, 2))}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="no-data">No audit logs found for the selected filters and time range.</p>
          )}
        </div>
      </div>
    );
  };

  const renderPoliciesTab = () => {
    return (
      <div className="governance-policies">
        <div className="policies-header">
          <h3>Access Policies</h3>
          <button 
            className="add-policy-button"
            onClick={() => setPolicyFormVisible(!policyFormVisible)}
          >
            {policyFormVisible ? 'Cancel' : 'Add New Policy'}
          </button>
        </div>
        
        {policyFormVisible && (
          <div className="policy-form">
            <h4>Create New Access Policy</h4>
            <div className="form-group">
              <label>Name:</label>
              <input 
                type="text" 
                value={newPolicy.name}
                onChange={(e) => handlePolicyChange('name', e.target.value)}
                placeholder="e.g., Medical Data Read Access"
              />
            </div>
            
            <div className="form-group">
              <label>Description:</label>
              <input 
                type="text" 
                value={newPolicy.description}
                onChange={(e) => handlePolicyChange('description', e.target.value)}
                placeholder="e.g., Read access to medical data for authorized users"
              />
            </div>
            
            <div className="form-group">
              <label>Resource Type:</label>
              <input 
                type="text" 
                value={newPolicy.resource_type}
                onChange={(e) => handlePolicyChange('resource_type', e.target.value)}
                placeholder="e.g., medical_data or * for all"
              />
            </div>
            
            <div className="form-group">
              <label>Actions (comma-separated):</label>
              <input 
                type="text" 
                value={newPolicy.actions.join(', ')}
                onChange={handleActionsChange}
                placeholder="e.g., read, update or * for all"
              />
            </div>
            
            <div className="form-group">
              <label>Conditions (JSON):</label>
              <textarea 
                value={JSON.stringify(newPolicy.conditions, null, 2)}
                onChange={handleConditionsChange}
                placeholder='e.g., {"role": ["doctor", "nurse"]}'
                rows={4}
              />
            </div>
            
            <div className="form-group">
              <label>Priority:</label>
              <input 
                type="number" 
                value={newPolicy.priority}
                onChange={(e) => handlePolicyChange('priority', parseInt(e.target.value))}
                placeholder="e.g., 50 (higher values take precedence)"
              />
            </div>
            
            <div className="form-actions">
              <button onClick={submitNewPolicy}>Create Policy</button>
              <button onClick={() => setPolicyFormVisible(false)}>Cancel</button>
            </div>
          </div>
        )}
        
        <div className="policies-list">
          {accessPolicies.length > 0 ? (
            <table className="policies-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Resource Type</th>
                  <th>Actions</th>
                  <th>Priority</th>
                  <th>Description</th>
                  <th>Conditions</th>
                </tr>
              </thead>
              <tbody>
                {accessPolicies.map((policy, index) => (
                  <tr key={index}>
                    <td>{policy.name}</td>
                    <td>{policy.resource_type}</td>
                    <td>{policy.actions.join(', ')}</td>
                    <td>{policy.priority}</td>
                    <td>{policy.description}</td>
                    <td>
                      <button 
                        className="details-button"
                        onClick={() => alert(JSON.stringify(policy.conditions, null, 2))}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="no-data">No access policies found.</p>
          )}
        </div>
      </div>
    );
  };

  const renderComplianceTab = () => {
    return (
      <div className="governance-compliance">
        <div className="compliance-summary">
          <h3>Compliance Status</h3>
          
          <div className="compliance-status-card">
            <div className={`compliance-status ${complianceStatus.overall_status || 'unknown'}`}>
              <h4>Overall Status</h4>
              <div className="status-indicator">
                {complianceStatus.overall_status || 'Unknown'}
              </div>
            </div>
            
            <div className="compliance-details">
              <div className="compliance-metric">
                <h4>HIPAA Compliance</h4>
                <div className={`status-indicator ${complianceStatus.hipaa_status || 'unknown'}`}>
                  {complianceStatus.hipaa_status || 'Unknown'}
                </div>
              </div>
              
              <div className="compliance-metric">
                <h4>Data Retention</h4>
                <div className={`status-indicator ${complianceStatus.data_retention_status || 'unknown'}`}>
                  {complianceStatus.data_retention_status || 'Unknown'}
                </div>
              </div>
              
              <div className="compliance-metric">
                <h4>Access Controls</h4>
                <div className={`status-indicator ${complianceStatus.access_control_status || 'unknown'}`}>
                  {complianceStatus.access_control_status || 'Unknown'}
                </div>
              </div>
              
              <div className="compliance-metric">
                <h4>Audit Logging</h4>
                <div className={`status-indicator ${complianceStatus.audit_logging_status || 'unknown'}`}>
                  {complianceStatus.audit_logging_status || 'Unknown'}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="compliance-issues">
          <h3>Compliance Issues</h3>
          
          {complianceStatus.issues && complianceStatus.issues.length > 0 ? (
            <table className="issues-table">
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Category</th>
                  <th>Description</th>
                  <th>Detected</th>
                  <th>Status</th>
                  <th>Remediation</th>
                </tr>
              </thead>
              <tbody>
                {complianceStatus.issues.map((issue, index) => (
                  <tr key={index} className={`severity-${issue.severity}`}>
                    <td className={`severity-${issue.severity}`}>{issue.severity}</td>
                    <td>{issue.category}</td>
                    <td>{issue.description}</td>
                    <td>{new Date(issue.detected_at * 1000).toLocaleString()}</td>
                    <td>{issue.status}</td>
                    <td>{issue.remediation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="no-data">No compliance issues detected.</p>
          )}
        </div>
        
        <div className="compliance-reports">
          <h3>Compliance Reports</h3>
          
          {complianceStatus.reports && complianceStatus.reports.length > 0 ? (
            <table className="reports-table">
              <thead>
                <tr>
                  <th>Report Type</th>
                  <th>Generated</th>
                  <th>Period</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {complianceStatus.reports.map((report, index) => (
                  <tr key={index}>
                    <td>{report.type}</td>
                    <td>{new Date(report.generated_at * 1000).toLocaleString()}</td>
                    <td>{report.period}</td>
                    <td className={`status-${report.status.toLowerCase()}`}>{report.status}</td>
                    <td>
                      <button className="download-button">Download</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="no-data">No compliance reports available.</p>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="governance-dashboard">
      <div className="governance-header">
        <h2>Governance Dashboard</h2>
        <div className="governance-controls">
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
            onClick={fetchGovernanceData}
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>
      
      <div className="governance-tabs">
        <div 
          className={`tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          Audit Logs
        </div>
        <div 
          className={`tab ${activeTab === 'policies' ? 'active' : ''}`}
          onClick={() => setActiveTab('policies')}
        >
          Access Policies
        </div>
        <div 
          className={`tab ${activeTab === 'compliance' ? 'active' : ''}`}
          onClick={() => setActiveTab('compliance')}
        >
          Compliance
        </div>
      </div>
      
      <div className="governance-content">
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <div>Loading governance data...</div>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {activeTab === 'audit' && renderAuditTab()}
        {activeTab === 'policies' && renderPoliciesTab()}
        {activeTab === 'compliance' && renderComplianceTab()}
      </div>
    </div>
  );
}

export default Governance;
