import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Component imports
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import DocumentManager from './components/DocumentManager';
import Monitoring from './components/Monitoring';
import Governance from './components/Governance';
import Settings from './components/Settings';
import Login from './components/Login';

// Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [systemHealth, setSystemHealth] = useState({});
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
    }
    
    // Check system health
    checkSystemHealth();
    
    // Set up interval to check system health periodically
    const healthInterval = setInterval(checkSystemHealth, 60000);
    
    setLoading(false);
    
    return () => {
      clearInterval(healthInterval);
    };
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Error checking system health:', error);
      setSystemHealth({ status: 'unhealthy', components: {} });
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <div className="header-left">
            <button className="menu-toggle" onClick={toggleSidebar}>
              ☰
            </button>
            <h1>Medical RAG Assistant</h1>
          </div>
          <div className="header-right">
            <div className={`system-status ${systemHealth.status || 'unknown'}`}>
              System: {systemHealth.status || 'Unknown'}
            </div>
            <div className="user-info">
              <span>{user.name}</span>
              <button onClick={handleLogout}>Logout</button>
            </div>
          </div>
        </header>
        
        <div className="app-container">
          <aside className={`app-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
            <nav>
              <ul>
                <li>
                  <Link to="/">Dashboard</Link>
                </li>
                <li>
                  <Link to="/chat">Chat Assistant</Link>
                </li>
                <li>
                  <Link to="/documents">Document Manager</Link>
                </li>
                {user.role === 'admin' && (
                  <>
                    <li>
                      <Link to="/monitoring">Monitoring</Link>
                    </li>
                    <li>
                      <Link to="/governance">Governance</Link>
                    </li>
                  </>
                )}
                <li>
                  <Link to="/settings">Settings</Link>
                </li>
              </ul>
            </nav>
          </aside>
          
          <main className="app-content">
            <Routes>
              <Route path="/" element={<Dashboard user={user} systemHealth={systemHealth} />} />
              <Route path="/chat" element={<ChatInterface user={user} />} />
              <Route path="/documents" element={<DocumentManager user={user} />} />
              {user.role === 'admin' && (
                <>
                  <Route path="/monitoring" element={<Monitoring />} />
                  <Route path="/governance" element={<Governance />} />
                </>
              )}
              <Route path="/settings" element={<Settings user={user} />} />
            </Routes>
          </main>
        </div>
        
        <footer className="app-footer">
          <p>Enhanced MLOps Framework for Agentic AI RAG Workflows &copy; 2025</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
