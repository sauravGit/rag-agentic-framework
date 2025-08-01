import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatInterface.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function ChatInterface({ user }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [streamingResponse, setStreamingResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true);
  const [showSources, setShowSources] = useState(true);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    // Generate a session ID if not already set
    if (!sessionId) {
      setSessionId(`session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`);
    }
    
    // Scroll to bottom when messages change
    scrollToBottom();
  }, [messages, streamingResponse]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };
    
    setMessages([...messages, userMessage]);
    setInput('');
    setError(null);
    
    try {
      if (useStreaming) {
        await handleStreamingQuery(input);
      } else {
        await handleStandardQuery(input);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to get a response. Please try again.');
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  const handleStandardQuery = async (query) => {
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/query`, {
        query,
        session_id: sessionId,
        user_id: user.id,
        stream: false,
        context: {
          domain: 'medical',
          user_role: user.role
        },
        metadata: {
          client_app: 'web_ui'
        }
      });
      
      // Add assistant message to chat
      const assistantMessage = {
        role: 'assistant',
        content: response.data.response_text,
        timestamp: new Date().toISOString(),
        sources: response.data.sources,
        metadata: response.data.metadata
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
      setIsLoading(false);
    } catch (error) {
      console.error('Error in standard query:', error);
      setError('Failed to get a response. Please try again.');
      setIsLoading(false);
      throw error;
    }
  };

  const handleStreamingQuery = async (query) => {
    setIsLoading(true);
    setIsStreaming(true);
    setStreamingResponse('');
    
    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/query/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          user_id: user.id,
          stream: true,
          context: {
            domain: 'medical',
            user_role: user.role
          },
          metadata: {
            client_app: 'web_ui'
          }
        }),
        signal: abortControllerRef.current.signal
      });
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let sources = [];
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            
            if (data.is_final && data.sources) {
              sources = data.sources;
            }
            
            setStreamingResponse(prev => prev + data.chunk_text);
          } catch (e) {
            console.error('Error parsing streaming chunk:', e);
          }
        }
      }
      
      // Add complete message to chat history
      const assistantMessage = {
        role: 'assistant',
        content: streamingResponse,
        timestamp: new Date().toISOString(),
        sources: sources,
        metadata: { streaming: true }
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
      setIsStreaming(false);
      setIsLoading(false);
      setStreamingResponse('');
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Streaming request was cancelled');
      } else {
        console.error('Error in streaming query:', error);
        setError('Failed to get a streaming response. Please try again.');
        setIsStreaming(false);
        setIsLoading(false);
        throw error;
      }
    }
  };

  const cancelStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
      setIsLoading(false);
    }
  };

  const renderSources = (sources) => {
    if (!sources || sources.length === 0 || !showSources) return null;
    
    return (
      <div className="message-sources">
        <h4>Sources:</h4>
        <ul>
          {sources.map((source, index) => (
            <li key={index}>
              <strong>{source.title}</strong>
              <p>{source.text}</p>
              <span className="source-score">Relevance: {(source.score * 100).toFixed(1)}%</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Medical Support Assistant</h2>
        <div className="chat-controls">
          <label>
            <input
              type="checkbox"
              checked={useStreaming}
              onChange={() => setUseStreaming(!useStreaming)}
            />
            Enable streaming
          </label>
          <label>
            <input
              type="checkbox"
              checked={showSources}
              onChange={() => setShowSources(!showSources)}
            />
            Show sources
          </label>
        </div>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>Welcome to the Medical Support Assistant</h3>
            <p>How can I help you with your medical questions today?</p>
            <p className="disclaimer">
              Disclaimer: This is an AI assistant for informational purposes only. 
              Always consult with a qualified healthcare provider for medical advice.
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-header">
                <span className="message-role">
                  {message.role === 'user' ? 'You' : 'Assistant'}
                </span>
                <span className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">
                {message.content}
              </div>
              {renderSources(message.sources)}
            </div>
          ))
        )}
        
        {isStreaming && (
          <div className="message assistant streaming">
            <div className="message-header">
              <span className="message-role">Assistant</span>
              <span className="message-time">Now</span>
            </div>
            <div className="message-content">
              {streamingResponse}
              <span className="cursor"></span>
            </div>
          </div>
        )}
        
        {isLoading && !isStreaming && (
          <div className="message-loading">
            <div className="loading-indicator">
              <div></div><div></div><div></div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="message-error">
            {error}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          placeholder="Type your medical question here..."
          disabled={isLoading}
        />
        {isStreaming ? (
          <button type="button" onClick={cancelStreaming} className="cancel-button">
            Cancel
          </button>
        ) : (
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        )}
      </form>
    </div>
  );
}

export default ChatInterface;
