// Web UI for Enhanced MLOps Framework for Agentic AI RAG Workflows
// This is a minimal React application for the web interface

import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [systemStatus, setSystemStatus] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [queryInput, setQueryInput] = useState('');
  const [queryResponse, setQueryResponse] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    // Fetch system status on component mount
    fetchSystemStatus();
    fetchDocuments();
    fetchMetrics();
  }, []);

  const fetchSystemStatus = async () => {
    setIsLoading(true);
    try {
      // In a real implementation, this would call the API Gateway
      // Mock implementation
      setTimeout(() => {
        setSystemStatus({
          status: 'healthy',
          components: {
            api_gateway: 'healthy',
            agent_orchestrator: 'healthy',
            document_processor: 'healthy',
            vector_db: 'healthy',
            compliance_service: 'healthy',
            evaluation_service: 'healthy',
            cost_optimizer: 'healthy'
          },
          version: '0.1.0'
        });
        setIsLoading(false);
      }, 500);
    } catch (error) {
      console.error('Error fetching system status:', error);
      setIsLoading(false);
    }
  };

  const fetchDocuments = async () => {
    // Mock implementation
    setTimeout(() => {
      setDocuments([
        { id: 'doc-1', title: 'Climate Change Report', status: 'processed', chunks: 15 },
        { id: 'doc-2', title: 'Economic Analysis 2025', status: 'processed', chunks: 23 },
        { id: 'doc-3', title: 'Healthcare Policy Overview', status: 'processing', chunks: 0 },
        { id: 'doc-4', title: 'AI Ethics Guidelines', status: 'processed', chunks: 8 },
        { id: 'doc-5', title: 'Renewable Energy Trends', status: 'processed', chunks: 12 }
      ]);
    }, 700);
  };

  const fetchMetrics = async () => {
    // Mock implementation
    setTimeout(() => {
      setMetrics({
        query_latency: {
          current: 245.3,
          trend: '-5%',
          threshold: 500
        },
        retrieval_precision: {
          current: 0.87,
          trend: '+2%',
          threshold: 0.7
        },
        token_usage: {
          current: 15243,
          trend: '+8%',
          threshold: 20000
        }
      });
    }, 600);
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!queryInput.trim()) return;

    // Mock query processing
    setQueryResponse({ loading: true });
    
    // Simulate API call delay
    setTimeout(() => {
      setQueryResponse({
        loading: false,
        answer: `This is a simulated response to: "${queryInput}"`,
        sources: [
          { title: 'Climate Change Report', relevance: 0.92 },
          { title: 'Renewable Energy Trends', relevance: 0.85 }
        ],
        reasoning: "1. Analyzed query\n2. Retrieved relevant documents\n3. Generated response"
      });
    }, 1500);
  };

  const renderDashboard = () => (
    <div className="dashboard">
      <h2>System Dashboard</h2>
      
      <div className="status-card">
        <h3>System Status: <span className={systemStatus.status === 'healthy' ? 'status-healthy' : 'status-error'}>{systemStatus.status}</span></h3>
        <div className="component-grid">
          {Object.entries(systemStatus.components || {}).map(([component, status]) => (
            <div key={component} className="component-item">
              <span className="component-name">{component.replace('_', ' ')}</span>
              <span className={`status-indicator ${status}`}>{status}</span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="metrics-card">
        <h3>Performance Metrics</h3>
        <div className="metrics-grid">
          {Object.entries(metrics).map(([metric, data]) => (
            <div key={metric} className="metric-item">
              <h4>{metric.replace('_', ' ')}</h4>
              <div className="metric-value">{data.current} <span className={data.trend.startsWith('+') ? 'trend-up' : 'trend-down'}>{data.trend}</span></div>
              <div className="metric-threshold">Threshold: {data.threshold}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderQueryInterface = () => (
    <div className="query-interface">
      <h2>Query Agent</h2>
      
      <form onSubmit={handleQuerySubmit} className="query-form">
        <input
          type="text"
          value={queryInput}
          onChange={(e) => setQueryInput(e.target.value)}
          placeholder="Ask a question..."
          className="query-input"
        />
        <button type="submit" className="query-button">Submit</button>
      </form>
      
      {queryResponse && (
        <div className="query-response">
          {queryResponse.loading ? (
            <div className="loading">Processing query...</div>
          ) : (
            <>
              <h3>Answer</h3>
              <div className="answer">{queryResponse.answer}</div>
              
              <h3>Sources</h3>
              <ul className="sources-list">
                {queryResponse.sources.map((source, index) => (
                  <li key={index} className="source-item">
                    <span className="source-title">{source.title}</span>
                    <span className="source-relevance">Relevance: {source.relevance.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
              
              <h3>Reasoning</h3>
              <div className="reasoning">{queryResponse.reasoning}</div>
            </>
          )}
        </div>
      )}
    </div>
  );

  const renderDocuments = () => (
    <div className="documents">
      <h2>Document Management</h2>
      
      <div className="upload-section">
        <h3>Upload New Document</h3>
        <div className="upload-form">
          <input type="file" className="file-input" />
          <button className="upload-button">Upload</button>
        </div>
      </div>
      
      <div className="documents-list">
        <h3>Processed Documents</h3>
        <table className="documents-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Status</th>
              <th>Chunks</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map(doc => (
              <tr key={doc.id}>
                <td>{doc.id}</td>
                <td>{doc.title}</td>
                <td><span className={`status-${doc.status}`}>{doc.status}</span></td>
                <td>{doc.chunks}</td>
                <td>
                  <button className="action-button">View</button>
                  <button className="action-button">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="app">
      <header className="header">
        <h1>Enhanced MLOps Framework for Agentic AI RAG Workflows</h1>
        <div className="nav-tabs">
          <button 
            className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={`tab ${activeTab === 'query' ? 'active' : ''}`}
            onClick={() => setActiveTab('query')}
          >
            Query Agent
          </button>
          <button 
            className={`tab ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            Documents
          </button>
        </div>
      </header>
      
      <main className="main-content">
        {isLoading ? (
          <div className="loading">Loading system status...</div>
        ) : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'query' && renderQueryInterface()}
            {activeTab === 'documents' && renderDocuments()}
          </>
        )}
      </main>
      
      <footer className="footer">
        <p>Enhanced MLOps Framework for Agentic AI RAG Workflows v0.1.0</p>
      </footer>
    </div>
  );
}

export default App;
