import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DocumentManager.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function DocumentManager({ user }) {
  const [documents, setDocuments] = useState([]);
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('all');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadFiles, setUploadFiles] = useState([]);
  const [processingStatus, setProcessingStatus] = useState({});
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showDocumentDetails, setShowDocumentDetails] = useState(false);

  useEffect(() => {
    fetchDocuments();
    fetchCollections();
  }, [selectedCollection]);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = { search: searchQuery || undefined };
      
      if (selectedCollection !== 'all') {
        params.collection_id = selectedCollection;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v1/documents`, { params });
      setDocuments(response.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Failed to fetch documents. Please try again.');
      setIsLoading(false);
    }
  };

  const fetchCollections = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/collections`);
      setCollections(response.data);
    } catch (error) {
      console.error('Error fetching collections:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchDocuments();
  };

  const handleFileChange = (e) => {
    setUploadFiles(Array.from(e.target.files));
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (uploadFiles.length === 0) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    setProcessingStatus({});
    
    const formData = new FormData();
    
    uploadFiles.forEach(file => {
      formData.append('files', file);
    });
    
    formData.append('collection_id', selectedCollection === 'all' ? '' : selectedCollection);
    formData.append('user_id', user.id);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      // Start polling for processing status
      const uploadId = response.data.upload_id;
      pollProcessingStatus(uploadId);
      
    } catch (error) {
      console.error('Error uploading documents:', error);
      setError('Failed to upload documents. Please try again.');
      setIsUploading(false);
    }
  };

  const pollProcessingStatus = async (uploadId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/documents/status/${uploadId}`);
        setProcessingStatus(response.data);
        
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(pollInterval);
          setIsUploading(false);
          
          if (response.data.status === 'completed') {
            setUploadFiles([]);
            setShowUploadForm(false);
            fetchDocuments();
          }
        }
      } catch (error) {
        console.error('Error polling processing status:', error);
        clearInterval(pollInterval);
        setIsUploading(false);
      }
    }, 2000);
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_BASE_URL}/api/v1/documents/${documentId}`);
      fetchDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      setError('Failed to delete document. Please try again.');
    }
  };

  const handleViewDocument = async (document) => {
    setSelectedDocument(document);
    setShowDocumentDetails(true);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getDocumentTypeIcon = (mimeType) => {
    if (mimeType.includes('pdf')) {
      return '📄';
    } else if (mimeType.includes('word') || mimeType.includes('docx')) {
      return '📝';
    } else if (mimeType.includes('excel') || mimeType.includes('xlsx')) {
      return '📊';
    } else if (mimeType.includes('image')) {
      return '🖼️';
    } else if (mimeType.includes('text')) {
      return '📃';
    } else {
      return '📁';
    }
  };

  const renderUploadForm = () => {
    return (
      <div className="upload-form">
        <h3>Upload Documents</h3>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label>Collection:</label>
            <select 
              value={selectedCollection} 
              onChange={(e) => setSelectedCollection(e.target.value)}
            >
              <option value="all">None (Default)</option>
              {collections.map(collection => (
                <option key={collection.id} value={collection.id}>
                  {collection.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Files:</label>
            <input 
              type="file" 
              multiple 
              onChange={handleFileChange}
              disabled={isUploading}
            />
            <div className="file-types">
              Supported formats: PDF, DOCX, TXT, CSV, XLSX, JPG, PNG
            </div>
          </div>
          
          {uploadFiles.length > 0 && (
            <div className="selected-files">
              <h4>Selected Files:</h4>
              <ul>
                {uploadFiles.map((file, index) => (
                  <li key={index}>
                    {file.name} ({formatFileSize(file.size)})
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {isUploading && (
            <div className="upload-progress">
              <div className="progress-bar">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <div className="progress-text">
                {uploadProgress < 100 ? 
                  `Uploading: ${uploadProgress}%` : 
                  'Processing documents...'
                }
              </div>
            </div>
          )}
          
          {processingStatus.status && (
            <div className={`processing-status ${processingStatus.status}`}>
              <div className="status-text">
                Status: {processingStatus.status}
              </div>
              {processingStatus.details && (
                <div className="status-details">
                  {processingStatus.details}
                </div>
              )}
              {processingStatus.progress && (
                <div className="progress-bar">
                  <div 
                    className="progress-bar-fill" 
                    style={{ width: `${processingStatus.progress}%` }}
                  ></div>
                </div>
              )}
            </div>
          )}
          
          <div className="form-actions">
            <button 
              type="submit" 
              disabled={isUploading || uploadFiles.length === 0}
            >
              Upload
            </button>
            <button 
              type="button" 
              onClick={() => setShowUploadForm(false)}
              disabled={isUploading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    );
  };

  const renderDocumentDetails = () => {
    if (!selectedDocument) return null;
    
    return (
      <div className="document-details-modal">
        <div className="document-details-content">
          <div className="document-details-header">
            <h3>{selectedDocument.title}</h3>
            <button 
              className="close-button"
              onClick={() => setShowDocumentDetails(false)}
            >
              ×
            </button>
          </div>
          
          <div className="document-details-body">
            <div className="document-metadata">
              <div className="metadata-item">
                <span className="metadata-label">File Name:</span>
                <span className="metadata-value">{selectedDocument.filename}</span>
              </div>
              
              <div className="metadata-item">
                <span className="metadata-label">Type:</span>
                <span className="metadata-value">{selectedDocument.mime_type}</span>
              </div>
              
              <div className="metadata-item">
                <span className="metadata-label">Size:</span>
                <span className="metadata-value">{formatFileSize(selectedDocument.file_size)}</span>
              </div>
              
              <div className="metadata-item">
                <span className="metadata-label">Uploaded:</span>
                <span className="metadata-value">{formatDate(selectedDocument.upload_date)}</span>
              </div>
              
              <div className="metadata-item">
                <span className="metadata-label">Collection:</span>
                <span className="metadata-value">
                  {selectedDocument.collection_name || 'None'}
                </span>
              </div>
              
              <div className="metadata-item">
                <span className="metadata-label">Status:</span>
                <span className={`metadata-value status-${selectedDocument.status}`}>
                  {selectedDocument.status}
                </span>
              </div>
            </div>
            
            {selectedDocument.chunks && selectedDocument.chunks.length > 0 && (
              <div className="document-chunks">
                <h4>Document Chunks ({selectedDocument.chunks.length})</h4>
                <div className="chunks-list">
                  {selectedDocument.chunks.map((chunk, index) => (
                    <div key={index} className="chunk-item">
                      <div className="chunk-header">
                        <span className="chunk-number">Chunk {index + 1}</span>
                        <span className="chunk-tokens">{chunk.token_count} tokens</span>
                      </div>
                      <div className="chunk-content">
                        {chunk.text.substring(0, 200)}
                        {chunk.text.length > 200 ? '...' : ''}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {selectedDocument.metadata && Object.keys(selectedDocument.metadata).length > 0 && (
              <div className="document-custom-metadata">
                <h4>Custom Metadata</h4>
                <div className="metadata-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Key</th>
                        <th>Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(selectedDocument.metadata).map(([key, value], index) => (
                        <tr key={index}>
                          <td>{key}</td>
                          <td>{typeof value === 'object' ? JSON.stringify(value) : value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
          
          <div className="document-details-footer">
            <button 
              className="download-button"
              onClick={() => window.open(`${API_BASE_URL}/api/v1/documents/${selectedDocument.id}/download`)}
            >
              Download
            </button>
            <button 
              className="delete-button"
              onClick={() => {
                handleDeleteDocument(selectedDocument.id);
                setShowDocumentDetails(false);
              }}
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="document-manager">
      <div className="document-manager-header">
        <h2>Document Manager</h2>
        <div className="document-controls">
          <form className="search-form" onSubmit={handleSearch}>
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents..."
            />
            <button type="submit">Search</button>
          </form>
          
          <div className="collection-filter">
            <label>Collection:</label>
            <select 
              value={selectedCollection} 
              onChange={(e) => setSelectedCollection(e.target.value)}
            >
              <option value="all">All Collections</option>
              {collections.map(collection => (
                <option key={collection.id} value={collection.id}>
                  {collection.name}
                </option>
              ))}
            </select>
          </div>
          
          <button 
            className="upload-button"
            onClick={() => setShowUploadForm(!showUploadForm)}
          >
            {showUploadForm ? 'Cancel Upload' : 'Upload Documents'}
          </button>
        </div>
      </div>
      
      {showUploadForm && renderUploadForm()}
      
      <div className="documents-list">
        {isLoading ? (
          <div className="loading-message">Loading documents...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : documents.length === 0 ? (
          <div className="empty-message">
            No documents found. Upload some documents to get started.
          </div>
        ) : (
          <table className="documents-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Title</th>
                <th>Collection</th>
                <th>Size</th>
                <th>Uploaded</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map(document => (
                <tr key={document.id}>
                  <td className="document-type">
                    {getDocumentTypeIcon(document.mime_type)}
                  </td>
                  <td className="document-title">{document.title}</td>
                  <td>{document.collection_name || 'None'}</td>
                  <td>{formatFileSize(document.file_size)}</td>
                  <td>{formatDate(document.upload_date)}</td>
                  <td className={`document-status status-${document.status}`}>
                    {document.status}
                  </td>
                  <td className="document-actions">
                    <button 
                      className="view-button"
                      onClick={() => handleViewDocument(document)}
                    >
                      View
                    </button>
                    <button 
                      className="delete-button"
                      onClick={() => handleDeleteDocument(document.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {showDocumentDetails && renderDocumentDetails()}
    </div>
  );
}

export default DocumentManager;
