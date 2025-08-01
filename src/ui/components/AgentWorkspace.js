import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AgentWorkspace.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function AgentWorkspace() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentConfig, setAgentConfig] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newAgentData, setNewAgentData] = useState({
    name: '',
    description: '',
    type: 'medical_assistant',
    model: 'gemini-pro',
    tools: [],
    config: {}
  });
  const [availableTools, setAvailableTools] = useState([]);
  const [testQuery, setTestQuery] = useState('');
  const [testResponse, setTestResponse] = useState(null);
  const [isTesting, setIsTesting] = useState(false);
  const [deploymentStatus, setDeploymentStatus] = useState({});

  useEffect(() => {
    fetchAgents();
    fetchAvailableTools();
  }, []);

  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/agents`);
      setAgents(response.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching agents:', error);
      setError('Failed to fetch agents. Please try again.');
      setIsLoading(false);
    }
  };

  const fetchAvailableTools = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/tools`);
      setAvailableTools(response.data);
    } catch (error) {
      console.error('Error fetching available tools:', error);
    }
  };

  const handleSelectAgent = async (agent) => {
    setSelectedAgent(agent);
    
    try {
      const configResponse = await axios.get(`${API_BASE_URL}/api/v1/agents/${agent.id}/config`);
      setAgentConfig(configResponse.data);
      
      const statusResponse = await axios.get(`${API_BASE_URL}/api/v1/agents/${agent.id}/status`);
      setDeploymentStatus(statusResponse.data);
    } catch (error) {
      console.error('Error fetching agent details:', error);
      setError('Failed to fetch agent details. Please try again.');
    }
  };

  const handleCreateAgent = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/agents`, newAgentData);
      setAgents([...agents, response.data]);
      setShowCreateForm(false);
      setNewAgentData({
        name: '',
        description: '',
        type: 'medical_assistant',
        model: 'gemini-pro',
        tools: [],
        config: {}
      });
    } catch (error) {
      console.error('Error creating agent:', error);
      setError('Failed to create agent. Please try again.');
    }
  };

  const handleDeleteAgent = async (agentId) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_BASE_URL}/api/v1/agents/${agentId}`);
      setAgents(agents.filter(agent => agent.id !== agentId));
      if (selectedAgent && selectedAgent.id === agentId) {
        setSelectedAgent(null);
        setAgentConfig({});
      }
    } catch (error) {
      console.error('Error deleting agent:', error);
      setError('Failed to delete agent. Please try again.');
    }
  };

  const handleUpdateAgentConfig = async () => {
    try {
      await axios.put(`${API_BASE_URL}/api/v1/agents/${selectedAgent.id}/config`, agentConfig);
      alert('Agent configuration updated successfully!');
    } catch (error) {
      console.error('Error updating agent configuration:', error);
      setError('Failed to update agent configuration. Please try again.');
    }
  };

  const handleDeployAgent = async () => {
    try {
      setDeploymentStatus({ status: 'deploying', message: 'Deploying agent...' });
      const response = await axios.post(`${API_BASE_URL}/api/v1/agents/${selectedAgent.id}/deploy`);
      setDeploymentStatus(response.data);
    } catch (error) {
      console.error('Error deploying agent:', error);
      setDeploymentStatus({ status: 'failed', message: 'Deployment failed. Please try again.' });
    }
  };

  const handleTestAgent = async () => {
    if (!testQuery.trim()) return;
    
    setIsTesting(true);
    setTestResponse(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/agents/${selectedAgent.id}/test`, {
        query: testQuery
      });
      setTestResponse(response.data);
    } catch (error) {
      console.error('Error testing agent:', error);
      setTestResponse({
        error: true,
        message: 'Failed to test agent. Please try again.'
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleToolSelection = (toolId) => {
    const isSelected = newAgentData.tools.includes(toolId);
    
    if (isSelected) {
      setNewAgentData({
        ...newAgentData,
        tools: newAgentData.tools.filter(id => id !== toolId)
      });
    } else {
      setNewAgentData({
        ...newAgentData,
        tools: [...newAgentData.tools, toolId]
      });
    }
  };

  const handleConfigChange = (key, value) => {
    setAgentConfig({
      ...agentConfig,
      [key]: value
    });
  };

  const renderCreateAgentForm = () => {
    return (
      <div className="create-agent-form">
        <h3>Create New Agent</h3>
        <div className="form-group">
          <label>Name:</label>
          <input 
            type="text" 
            value={newAgentData.name}
            onChange={(e) => setNewAgentData({ ...newAgentData, name: e.target.value })}
            placeholder="e.g., Medical Support Assistant"
          />
        </div>
        
        <div className="form-group">
          <label>Description:</label>
          <textarea 
            value={newAgentData.description}
            onChange={(e) => setNewAgentData({ ...newAgentData, description: e.target.value })}
            placeholder="Describe what this agent does..."
            rows={3}
          />
        </div>
        
        <div className="form-group">
          <label>Type:</label>
          <select
            value={newAgentData.type}
            onChange={(e) => setNewAgentData({ ...newAgentData, type: e.target.value })}
          >
            <option value="medical_assistant">Medical Assistant</option>
            <option value="document_analyzer">Document Analyzer</option>
            <option value="research_assistant">Research Assistant</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Model:</label>
          <select
            value={newAgentData.model}
            onChange={(e) => setNewAgentData({ ...newAgentData, model: e.target.value })}
          >
            <option value="gemini-pro">Gemini Pro</option>
            <option value="gemini-ultra">Gemini Ultra</option>
            <option value="claude-3-opus">Claude 3 Opus</option>
            <option value="gpt-4">GPT-4</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Tools:</label>
          <div className="tools-selection">
            {availableTools.map(tool => (
              <div key={tool.id} className="tool-option">
                <input 
                  type="checkbox"
                  id={`tool-${tool.id}`}
                  checked={newAgentData.tools.includes(tool.id)}
                  onChange={() => handleToolSelection(tool.id)}
                />
                <label htmlFor={`tool-${tool.id}`}>
                  {tool.name} - {tool.description}
                </label>
              </div>
            ))}
          </div>
        </div>
        
        <div className="form-actions">
          <button onClick={handleCreateAgent}>Create Agent</button>
          <button onClick={() => setShowCreateForm(false)}>Cancel</button>
        </div>
      </div>
    );
  };

  const renderAgentDetails = () => {
    if (!selectedAgent) return null;
    
    return (
      <div className="agent-details">
        <div className="agent-header">
          <h3>{selectedAgent.name}</h3>
          <div className="agent-status">
            <span className={`status-indicator ${selectedAgent.status}`}>
              {selectedAgent.status}
            </span>
          </div>
        </div>
        
        <div className="agent-info">
          <div className="info-item">
            <span className="info-label">Type:</span>
            <span className="info-value">{selectedAgent.type}</span>
          </div>
          
          <div className="info-item">
            <span className="info-label">Model:</span>
            <span className="info-value">{selectedAgent.model}</span>
          </div>
          
          <div className="info-item">
            <span className="info-label">Created:</span>
            <span className="info-value">
              {new Date(selectedAgent.created_at).toLocaleString()}
            </span>
          </div>
          
          <div className="info-item">
            <span className="info-label">Last Updated:</span>
            <span className="info-value">
              {new Date(selectedAgent.updated_at).toLocaleString()}
            </span>
          </div>
        </div>
        
        <div className="agent-description">
          <h4>Description</h4>
          <p>{selectedAgent.description}</p>
        </div>
        
        <div className="agent-tools">
          <h4>Tools</h4>
          {selectedAgent.tools && selectedAgent.tools.length > 0 ? (
            <ul className="tools-list">
              {selectedAgent.tools.map((toolId, index) => {
                const tool = availableTools.find(t => t.id === toolId);
                return (
                  <li key={index} className="tool-item">
                    {tool ? tool.name : toolId}
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="no-data">No tools configured.</p>
          )}
        </div>
        
        <div className="agent-configuration">
          <h4>Configuration</h4>
          {Object.keys(agentConfig).length > 0 ? (
            <div className="config-editor">
              {Object.entries(agentConfig).map(([key, value], index) => (
                <div key={index} className="config-item">
                  <label>{key}:</label>
                  {typeof value === 'boolean' ? (
                    <select
                      value={value.toString()}
                      onChange={(e) => handleConfigChange(key, e.target.value === 'true')}
                    >
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                  ) : typeof value === 'number' ? (
                    <input 
                      type="number"
                      value={value}
                      onChange={(e) => handleConfigChange(key, parseFloat(e.target.value))}
                    />
                  ) : typeof value === 'object' ? (
                    <textarea
                      value={JSON.stringify(value, null, 2)}
                      onChange={(e) => {
                        try {
                          handleConfigChange(key, JSON.parse(e.target.value));
                        } catch (error) {
                          // Invalid JSON, but don't show error until submit
                          console.log('Invalid JSON for', key);
                        }
                      }}
                      rows={4}
                    />
                  ) : (
                    <input 
                      type="text"
                      value={value}
                      onChange={(e) => handleConfigChange(key, e.target.value)}
                    />
                  )}
                </div>
              ))}
              <button 
                className="update-config-button"
                onClick={handleUpdateAgentConfig}
              >
                Update Configuration
              </button>
            </div>
          ) : (
            <p className="no-data">No configuration available.</p>
          )}
        </div>
        
        <div className="agent-deployment">
          <h4>Deployment</h4>
          <div className="deployment-status">
            <div className={`status-indicator ${deploymentStatus.status || 'unknown'}`}>
              {deploymentStatus.status || 'Unknown'}
            </div>
            {deploymentStatus.message && (
              <div className="status-message">{deploymentStatus.message}</div>
            )}
          </div>
          
          <div className="deployment-actions">
            <button 
              className="deploy-button"
              onClick={handleDeployAgent}
              disabled={deploymentStatus.status === 'deploying'}
            >
              {deploymentStatus.status === 'deployed' ? 'Redeploy' : 'Deploy'}
            </button>
          </div>
        </div>
        
        <div className="agent-testing">
          <h4>Test Agent</h4>
          <div className="test-input">
            <input 
              type="text"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              placeholder="Enter a test query..."
              disabled={isTesting}
            />
            <button 
              onClick={handleTestAgent}
              disabled={isTesting || !testQuery.trim()}
            >
              {isTesting ? 'Testing...' : 'Test'}
            </button>
          </div>
          
          {testResponse && (
            <div className={`test-response ${testResponse.error ? 'error' : ''}`}>
              <h5>Response:</h5>
              {testResponse.error ? (
                <div className="error-message">{testResponse.message}</div>
              ) : (
                <>
                  <div className="response-content">{testResponse.response}</div>
                  {testResponse.metadata && (
                    <div className="response-metadata">
                      <h6>Metadata:</h6>
                      <pre>{JSON.stringify(testResponse.metadata, null, 2)}</pre>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
        
        <div className="agent-actions">
          <button 
            className="delete-button"
            onClick={() => handleDeleteAgent(selectedAgent.id)}
          >
            Delete Agent
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="agent-workspace">
      <div className="workspace-header">
        <h2>Agent Workspace</h2>
        <button 
          className="create-agent-button"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : 'Create New Agent'}
        </button>
      </div>
      
      {showCreateForm && renderCreateAgentForm()}
      
      <div className="workspace-content">
        <div className="agents-sidebar">
          <h3>Your Agents</h3>
          {isLoading ? (
            <div className="loading-message">Loading agents...</div>
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : agents.length === 0 ? (
            <div className="empty-message">
              No agents found. Create your first agent to get started.
            </div>
          ) : (
            <ul className="agents-list">
              {agents.map(agent => (
                <li 
                  key={agent.id} 
                  className={`agent-item ${selectedAgent && selectedAgent.id === agent.id ? 'selected' : ''}`}
                  onClick={() => handleSelectAgent(agent)}
                >
                  <div className="agent-name">{agent.name}</div>
                  <div className="agent-type">{agent.type}</div>
                  <div className={`agent-status ${agent.status}`}>{agent.status}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <div className="agent-detail-panel">
          {selectedAgent ? renderAgentDetails() : (
            <div className="no-selection-message">
              Select an agent from the list or create a new one to get started.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AgentWorkspace;
