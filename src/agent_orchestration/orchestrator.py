"""
Agent Orchestrator for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides the main orchestration layer for managing and coordinating
multiple agents, tools, and workflows in the RAG system.
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Local imports
from ..core.config import Config
from .adk_integration import ADKIntegration
from .agentspace_integration import AgentspaceIntegration

class AgentOrchestrator:
    """Orchestrates multiple agents and tools for complex RAG workflows."""
    
    def __init__(self, config: Config):
        """Initialize the Agent Orchestrator.
        
        Args:
            config: Configuration object containing orchestration settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations
        self.adk = ADKIntegration(config)
        self.agentspace = AgentspaceIntegration(config)
        
        # Track active sessions
        self.active_sessions = {}
        
        # Load agent configurations
        self.agent_configs = self._load_agent_configs()
        
        # Initialize tool registry
        self.tool_registry = self._initialize_tool_registry()
        
        self.logger.info("Agent Orchestrator initialized")
    
    def _load_agent_configs(self) -> Dict[str, Any]:
        """Load agent configurations from config files.
        
        Returns:
            Dict containing agent configurations
        """
        agent_configs = {}
        
        try:
            # Get agent config path from main config
            agent_config_path = self.config.get("agent_orchestration.config_path", "config/agents")
            
            # Ensure path is absolute
            if not os.path.isabs(agent_config_path):
                base_path = self.config.get("core.base_path", os.getcwd())
                agent_config_path = os.path.join(base_path, agent_config_path)
            
            # Load all JSON files in the directory
            if os.path.exists(agent_config_path):
                for filename in os.listdir(agent_config_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(agent_config_path, filename)
                        with open(file_path, 'r') as f:
                            agent_config = json.load(f)
                            agent_id = agent_config.get('id') or os.path.splitext(filename)[0]
                            agent_configs[agent_id] = agent_config
            
            self.logger.info(f"Loaded {len(agent_configs)} agent configurations")
            
        except Exception as e:
            self.logger.error(f"Error loading agent configurations: {str(e)}")
        
        return agent_configs
    
    def _initialize_tool_registry(self) -> Dict[str, Any]:
        """Initialize the tool registry with available tools.
        
        Returns:
            Dict containing registered tools
        """
        tool_registry = {}
        
        try:
            # Get tool registry path from main config
            tool_registry_path = self.config.get("agent_orchestration.tool_registry_path", "config/tools")
            
            # Ensure path is absolute
            if not os.path.isabs(tool_registry_path):
                base_path = self.config.get("core.base_path", os.getcwd())
                tool_registry_path = os.path.join(base_path, tool_registry_path)
            
            # Load all JSON files in the directory
            if os.path.exists(tool_registry_path):
                for filename in os.listdir(tool_registry_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(tool_registry_path, filename)
                        with open(file_path, 'r') as f:
                            tool_config = json.load(f)
                            tool_id = tool_config.get('id') or os.path.splitext(filename)[0]
                            tool_registry[tool_id] = tool_config
            
            self.logger.info(f"Loaded {len(tool_registry)} tools in registry")
            
        except Exception as e:
            self.logger.error(f"Error initializing tool registry: {str(e)}")
        
        return tool_registry
    
    def create_session(self, user_id: str, session_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new agent session.
        
        Args:
            user_id: ID of the user creating the session
            session_metadata: Additional metadata for the session (optional)
            
        Returns:
            Dict containing session details
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        session = {
            "id": session_id,
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "status": "active",
            "metadata": session_metadata or {},
            "history": [],
            "agents": {},
            "context": {}
        }
        
        self.active_sessions[session_id] = session
        self.logger.info(f"Created session {session_id} for user {user_id}")
        
        return {
            "session_id": session_id,
            "created_at": timestamp,
            "status": "active"
        }
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End an active agent session.
        
        Args:
            session_id: ID of the session to end
            
        Returns:
            Dict containing session details
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session["status"] = "ended"
        session["updated_at"] = datetime.now().isoformat()
        
        # Archive session (in a real implementation, this would persist to storage)
        # For now, we'll just remove it from active sessions
        session_data = self.active_sessions.pop(session_id)
        
        self.logger.info(f"Ended session {session_id}")
        
        return {
            "session_id": session_id,
            "ended_at": session_data["updated_at"],
            "status": "ended",
            "message_count": len(session_data["history"])
        }
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get details of an active session.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Dict containing session details
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "status": session["status"],
            "message_count": len(session["history"]),
            "active_agents": list(session["agents"].keys())
        }
    
    def process_query(self, 
                     session_id: str, 
                     query: str, 
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user query through the agent orchestration system.
        
        Args:
            session_id: ID of the session for this query
            query: User query text
            context: Additional context for this query (optional)
            
        Returns:
            Dict containing the response and metadata
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Update session
        timestamp = datetime.now().isoformat()
        session["updated_at"] = timestamp
        
        # Add query to history
        query_entry = {
            "role": "user",
            "content": query,
            "timestamp": timestamp
        }
        session["history"].append(query_entry)
        
        # Update context
        if context:
            session["context"].update(context)
        
        # Determine which agent(s) to use for this query
        primary_agent_id = self._select_primary_agent(query, session)
        
        # Process with primary agent
        try:
            # Check if we need to create the agent in the session
            if primary_agent_id not in session["agents"]:
                self._initialize_agent_in_session(primary_agent_id, session)
            
            # Get agent details
            agent_details = session["agents"][primary_agent_id]
            
            # Execute the agent
            if agent_details["provider"] == "adk":
                # Use ADK integration
                response = self.adk.execute_agent(
                    agent_id=agent_details["external_id"],
                    query=query,
                    context=session["context"]
                )
            else:
                # Use local agent implementation
                response = self._execute_local_agent(
                    agent_id=primary_agent_id,
                    query=query,
                    session=session
                )
            
            # Add response to history
            response_entry = {
                "role": "assistant",
                "content": response["response"],
                "timestamp": datetime.now().isoformat(),
                "metadata": response.get("metadata", {})
            }
            session["history"].append(response_entry)
            
            # Return the response
            return {
                "response": response["response"],
                "session_id": session_id,
                "agent_id": primary_agent_id,
                "metadata": response.get("metadata", {}),
                "timestamp": response_entry["timestamp"]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query in session {session_id}: {str(e)}")
            
            # Add error to history
            error_entry = {
                "role": "system",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            session["history"].append(error_entry)
            
            # Return error response
            return {
                "error": True,
                "message": f"Failed to process query: {str(e)}",
                "session_id": session_id
            }
    
    def _select_primary_agent(self, query: str, session: Dict[str, Any]) -> str:
        """Select the primary agent to handle a query.
        
        Args:
            query: User query text
            session: Session object
            
        Returns:
            ID of the selected agent
        """
        # For now, use a simple approach - use the default agent or the first available
        default_agent_id = self.config.get("agent_orchestration.default_agent_id")
        
        if default_agent_id and default_agent_id in self.agent_configs:
            return default_agent_id
        
        # If no default or it doesn't exist, use the first available
        if self.agent_configs:
            return next(iter(self.agent_configs.keys()))
        
        # If no agents are configured, raise an error
        raise ValueError("No agents available for processing query")
    
    def _initialize_agent_in_session(self, agent_id: str, session: Dict[str, Any]) -> None:
        """Initialize an agent in the session.
        
        Args:
            agent_id: ID of the agent to initialize
            session: Session object
        """
        if agent_id not in self.agent_configs:
            raise ValueError(f"Agent {agent_id} not found in configurations")
        
        agent_config = self.agent_configs[agent_id]
        
        # Determine if this is an external (ADK) or local agent
        provider = agent_config.get("provider", "local")
        
        if provider == "adk":
            # Check if the agent exists in ADK
            try:
                adk_agent = self.adk.get_agent(agent_config["external_id"])
                external_id = agent_config["external_id"]
            except:
                # Create the agent in ADK
                adk_agent = self.adk.create_agent(
                    name=agent_config["name"],
                    description=agent_config["description"],
                    model=agent_config.get("model", "gemini-pro"),
                    tools=agent_config.get("tools", [])
                )
                external_id = adk_agent["id"]
                
                # Update the agent config with the external ID
                agent_config["external_id"] = external_id
            
            # Add to session
            session["agents"][agent_id] = {
                "id": agent_id,
                "external_id": external_id,
                "provider": "adk",
                "name": agent_config["name"],
                "initialized_at": datetime.now().isoformat()
            }
        else:
            # Local agent
            session["agents"][agent_id] = {
                "id": agent_id,
                "provider": "local",
                "name": agent_config["name"],
                "initialized_at": datetime.now().isoformat(),
                "state": {}
            }
    
    def _execute_local_agent(self, 
                           agent_id: str, 
                           query: str, 
                           session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a local agent implementation.
        
        Args:
            agent_id: ID of the agent to execute
            query: User query text
            session: Session object
            
        Returns:
            Dict containing the response and metadata
        """
        agent_config = self.agent_configs[agent_id]
        agent_state = session["agents"][agent_id].get("state", {})
        
        # In a real implementation, this would use a local LLM or API call
        # For now, we'll return a simple response
        response = {
            "response": f"This is a simulated response from the {agent_config['name']} agent for query: {query}",
            "metadata": {
                "agent_id": agent_id,
                "model": agent_config.get("model", "simulated"),
                "processing_time": 0.5,
                "tool_calls": []
            }
        }
        
        return response
    
    def register_tool(self, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new tool in the tool registry.
        
        Args:
            tool_config: Configuration for the tool
            
        Returns:
            Dict containing the registered tool details
        """
        if "id" not in tool_config:
            tool_config["id"] = str(uuid.uuid4())
        
        tool_id = tool_config["id"]
        
        # Validate required fields
        required_fields = ["name", "description", "function_schema"]
        for field in required_fields:
            if field not in tool_config:
                raise ValueError(f"Missing required field '{field}' in tool configuration")
        
        # Add to registry
        self.tool_registry[tool_id] = tool_config
        
        # Save to file (in a real implementation)
        # For now, just log
        self.logger.info(f"Registered tool {tool_id}: {tool_config['name']}")
        
        return {
            "id": tool_id,
            "name": tool_config["name"],
            "status": "registered"
        }
    
    def get_tool(self, tool_id: str) -> Dict[str, Any]:
        """Get a tool from the registry.
        
        Args:
            tool_id: ID of the tool to retrieve
            
        Returns:
            Dict containing the tool configuration
        """
        if tool_id not in self.tool_registry:
            raise ValueError(f"Tool {tool_id} not found in registry")
        
        return self.tool_registry[tool_id]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools in the registry.
        
        Returns:
            List of dicts containing tool details
        """
        return [
            {
                "id": tool_id,
                "name": tool_config["name"],
                "description": tool_config["description"],
                "category": tool_config.get("category", "general")
            }
            for tool_id, tool_config in self.tool_registry.items()
        ]
    
    def create_agent(self, 
                    name: str, 
                    description: str, 
                    agent_type: str = "rag",
                    model: str = "gemini-pro",
                    tools: List[str] = None,
                    config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new agent configuration.
        
        Args:
            name: Name of the agent
            description: Description of the agent's purpose
            agent_type: Type of agent (e.g., "rag", "chat", "custom")
            model: Model to use for the agent
            tools: List of tool IDs to enable for the agent
            config: Additional configuration for the agent
            
        Returns:
            Dict containing the created agent details
        """
        agent_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Validate tools
        validated_tools = []
        if tools:
            for tool_id in tools:
                if tool_id in self.tool_registry:
                    validated_tools.append(tool_id)
                else:
                    self.logger.warning(f"Tool {tool_id} not found in registry, skipping")
        
        # Create agent configuration
        agent_config = {
            "id": agent_id,
            "name": name,
            "description": description,
            "type": agent_type,
            "model": model,
            "tools": validated_tools,
            "config": config or {},
            "created_at": timestamp,
            "updated_at": timestamp,
            "provider": "local"  # Default to local
        }
        
        # Add to configurations
        self.agent_configs[agent_id] = agent_config
        
        # Save to file (in a real implementation)
        # For now, just log
        self.logger.info(f"Created agent {agent_id}: {name}")
        
        return {
            "id": agent_id,
            "name": name,
            "type": agent_type,
            "status": "created"
        }
    
    def update_agent(self, 
                    agent_id: str, 
                    name: str = None,
                    description: str = None,
                    model: str = None,
                    tools: List[str] = None,
                    config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an existing agent configuration.
        
        Args:
            agent_id: ID of the agent to update
            name: Updated name (if provided)
            description: Updated description (if provided)
            model: Updated model (if provided)
            tools: Updated tools list (if provided)
            config: Updated configuration (if provided)
            
        Returns:
            Dict containing the updated agent details
        """
        if agent_id not in self.agent_configs:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_config = self.agent_configs[agent_id]
        timestamp = datetime.now().isoformat()
        
        # Update fields if provided
        if name is not None:
            agent_config["name"] = name
            
        if description is not None:
            agent_config["description"] = description
            
        if model is not None:
            agent_config["model"] = model
            
        if tools is not None:
            # Validate tools
            validated_tools = []
            for tool_id in tools:
                if tool_id in self.tool_registry:
                    validated_tools.append(tool_id)
                else:
                    self.logger.warning(f"Tool {tool_id} not found in registry, skipping")
            
            agent_config["tools"] = validated_tools
            
        if config is not None:
            agent_config["config"] = config
        
        agent_config["updated_at"] = timestamp
        
        # If this is an ADK agent, update it there too
        if agent_config.get("provider") == "adk" and "external_id" in agent_config:
            try:
                self.adk.update_agent(
                    agent_id=agent_config["external_id"],
                    display_name=agent_config["name"],
                    description=agent_config["description"],
                    model=agent_config["model"]
                )
            except Exception as e:
                self.logger.error(f"Error updating ADK agent {agent_id}: {str(e)}")
        
        # Save to file (in a real implementation)
        # For now, just log
        self.logger.info(f"Updated agent {agent_id}")
        
        return {
            "id": agent_id,
            "name": agent_config["name"],
            "updated_at": timestamp,
            "status": "updated"
        }
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent configuration.
        
        Args:
            agent_id: ID of the agent to delete
            
        Returns:
            Dict containing the result
        """
        if agent_id not in self.agent_configs:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_config = self.agent_configs[agent_id]
        
        # If this is an ADK agent, delete it there too
        if agent_config.get("provider") == "adk" and "external_id" in agent_config:
            try:
                self.adk.delete_agent(agent_config["external_id"])
            except Exception as e:
                self.logger.error(f"Error deleting ADK agent {agent_id}: {str(e)}")
        
        # Remove from configurations
        del self.agent_configs[agent_id]
        
        # Save to file (in a real implementation)
        # For now, just log
        self.logger.info(f"Deleted agent {agent_id}")
        
        return {
            "id": agent_id,
            "status": "deleted"
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agent configurations.
        
        Returns:
            List of dicts containing agent details
        """
        return [
            {
                "id": agent_id,
                "name": agent_config["name"],
                "description": agent_config["description"],
                "type": agent_config.get("type", "unknown"),
                "model": agent_config.get("model", "unknown"),
                "provider": agent_config.get("provider", "local"),
                "created_at": agent_config.get("created_at"),
                "updated_at": agent_config.get("updated_at"),
                "status": "active"
            }
            for agent_id, agent_config in self.agent_configs.items()
        ]
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get an agent configuration.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Dict containing the agent details
        """
        if agent_id not in self.agent_configs:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_config = self.agent_configs[agent_id]
        
        return {
            "id": agent_id,
            "name": agent_config["name"],
            "description": agent_config["description"],
            "type": agent_config.get("type", "unknown"),
            "model": agent_config.get("model", "unknown"),
            "tools": agent_config.get("tools", []),
            "provider": agent_config.get("provider", "local"),
            "created_at": agent_config.get("created_at"),
            "updated_at": agent_config.get("updated_at"),
            "status": "active"
        }
    
    def deploy_agent(self, agent_id: str) -> Dict[str, Any]:
        """Deploy an agent for serving.
        
        Args:
            agent_id: ID of the agent to deploy
            
        Returns:
            Dict containing deployment status
        """
        if agent_id not in self.agent_configs:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_config = self.agent_configs[agent_id]
        
        # If this is an ADK agent, deploy it there
        if agent_config.get("provider") == "adk" and "external_id" in agent_config:
            try:
                deployment_status = self.adk.deploy_agent(agent_config["external_id"])
                return deployment_status
            except Exception as e:
                self.logger.error(f"Error deploying ADK agent {agent_id}: {str(e)}")
                return {
                    "status": "failed",
                    "message": f"Deployment failed: {str(e)}",
                    "agent_id": agent_id
                }
        
        # For local agents, mark as deployed
        agent_config["deployed"] = True
        agent_config["deployed_at"] = datetime.now().isoformat()
        
        return {
            "status": "deployed",
            "message": "Agent is ready for serving",
            "agent_id": agent_id
        }
    
    def get_deployment_status(self, agent_id: str) -> Dict[str, Any]:
        """Get the deployment status of an agent.
        
        Args:
            agent_id: ID of the agent to check
            
        Returns:
            Dict containing deployment status
        """
        if agent_id not in self.agent_configs:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_config = self.agent_configs[agent_id]
        
        # If this is an ADK agent, check status there
        if agent_config.get("provider") == "adk" and "external_id" in agent_config:
            try:
                return self.adk.get_deployment_status(agent_config["external_id"])
            except Exception as e:
                self.logger.error(f"Error getting deployment status for ADK agent {agent_id}: {str(e)}")
                return {
                    "status": "unknown",
                    "message": f"Failed to determine status: {str(e)}",
                    "agent_id": agent_id
                }
        
        # For local agents, check deployed flag
        if agent_config.get("deployed", False):
            return {
                "status": "deployed",
                "message": "Agent is ready for serving",
                "agent_id": agent_id,
                "deployed_at": agent_config.get("deployed_at")
            }
        else:
            return {
                "status": "not_deployed",
                "message": "Agent is not deployed",
                "agent_id": agent_id
            }
