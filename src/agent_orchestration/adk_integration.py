"""
Google Agent Development Kit (ADK) integration module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides integration with Google's Agent Development Kit (ADK) for building,
managing, and orchestrating multi-agent systems with advanced capabilities.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

# Import ADK components
try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import Agent
    from google.cloud.aiplatform.agents import AgentServiceClient
    from google.cloud.aiplatform.agents import Tool, ToolConfig
    from google.cloud.aiplatform.agents import AgentContext, AgentResponse
except ImportError:
    logging.warning("Google Cloud AI Platform SDK not installed. ADK integration will not be available.")

# Local imports
from ..core.config import Config

class ADKIntegration:
    """Integration with Google's Agent Development Kit (ADK)."""
    
    def __init__(self, config: Config):
        """Initialize the ADK integration.
        
        Args:
            config: Configuration object containing ADK settings
        """
        self.config = config
        self.project_id = config.get("gcp.project_id")
        self.location = config.get("gcp.location", "us-central1")
        self.agent_service_client = None
        self.initialized = False
        
        # Initialize ADK if available
        if "google.cloud.aiplatform" in globals():
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                self.agent_service_client = AgentServiceClient()
                self.initialized = True
                logging.info(f"ADK integration initialized for project {self.project_id} in {self.location}")
            except Exception as e:
                logging.error(f"Failed to initialize ADK: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if ADK integration is available.
        
        Returns:
            bool: True if ADK is available, False otherwise
        """
        return self.initialized
    
    def create_agent(self, 
                    name: str, 
                    description: str, 
                    display_name: str = None,
                    model: str = "gemini-pro",
                    tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new agent using ADK.
        
        Args:
            name: Unique name for the agent
            description: Description of the agent's purpose and capabilities
            display_name: Human-readable display name (defaults to name if not provided)
            model: Model to use for the agent (default: gemini-pro)
            tools: List of tool configurations for the agent
            
        Returns:
            Dict containing the created agent details
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        display_name = display_name or name
        
        # Convert tool configurations to ADK Tool objects
        adk_tools = []
        if tools:
            for tool_config in tools:
                tool = Tool(
                    name=tool_config.get("name"),
                    description=tool_config.get("description", ""),
                    function_declarations=tool_config.get("function_declarations", [])
                )
                adk_tools.append(tool)
        
        try:
            # Create the agent
            agent = Agent.create(
                display_name=display_name,
                description=description,
                tools=adk_tools if adk_tools else None,
                model=model
            )
            
            # Return agent details
            agent_details = {
                "id": agent.name.split("/")[-1],
                "name": name,
                "display_name": display_name,
                "description": description,
                "model": model,
                "tools": tools or [],
                "created_at": agent.create_time.isoformat() if hasattr(agent, 'create_time') else None,
                "updated_at": agent.update_time.isoformat() if hasattr(agent, 'update_time') else None,
                "status": "created"
            }
            
            logging.info(f"Created agent: {agent_details['id']}")
            return agent_details
            
        except Exception as e:
            logging.error(f"Failed to create agent: {str(e)}")
            raise
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get details of an existing agent.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Dict containing the agent details
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        try:
            agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            agent = Agent(agent_name)
            
            # Return agent details
            return {
                "id": agent_id,
                "name": agent.display_name,
                "display_name": agent.display_name,
                "description": agent.description,
                "model": agent.model,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "function_declarations": tool.function_declarations
                    }
                    for tool in agent.tools
                ] if hasattr(agent, 'tools') else [],
                "created_at": agent.create_time.isoformat() if hasattr(agent, 'create_time') else None,
                "updated_at": agent.update_time.isoformat() if hasattr(agent, 'update_time') else None,
                "status": "active"
            }
            
        except Exception as e:
            logging.error(f"Failed to get agent {agent_id}: {str(e)}")
            raise
    
    def update_agent(self, 
                    agent_id: str, 
                    description: str = None,
                    display_name: str = None,
                    model: str = None,
                    tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update an existing agent.
        
        Args:
            agent_id: ID of the agent to update
            description: Updated description (if provided)
            display_name: Updated display name (if provided)
            model: Updated model (if provided)
            tools: Updated tools list (if provided)
            
        Returns:
            Dict containing the updated agent details
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        try:
            agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            agent = Agent(agent_name)
            
            # Update fields if provided
            update_mask = []
            
            if display_name is not None:
                agent.display_name = display_name
                update_mask.append("display_name")
                
            if description is not None:
                agent.description = description
                update_mask.append("description")
                
            if model is not None:
                agent.model = model
                update_mask.append("model")
                
            if tools is not None:
                # Convert tool configurations to ADK Tool objects
                adk_tools = []
                for tool_config in tools:
                    tool = Tool(
                        name=tool_config.get("name"),
                        description=tool_config.get("description", ""),
                        function_declarations=tool_config.get("function_declarations", [])
                    )
                    adk_tools.append(tool)
                
                agent.tools = adk_tools
                update_mask.append("tools")
            
            # Update the agent if there are changes
            if update_mask:
                agent.update(update_mask=update_mask)
            
            # Return updated agent details
            return self.get_agent(agent_id)
            
        except Exception as e:
            logging.error(f"Failed to update agent {agent_id}: {str(e)}")
            raise
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.
        
        Args:
            agent_id: ID of the agent to delete
            
        Returns:
            bool: True if deletion was successful
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        try:
            agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            Agent(agent_name).delete()
            logging.info(f"Deleted agent: {agent_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete agent {agent_id}: {str(e)}")
            raise
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents in the project.
        
        Returns:
            List of dicts containing agent details
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        try:
            agents = Agent.list(
                project=self.project_id,
                location=self.location
            )
            
            # Convert to list of dicts
            agent_list = []
            for agent in agents:
                agent_id = agent.name.split("/")[-1]
                agent_list.append({
                    "id": agent_id,
                    "name": agent.display_name,
                    "display_name": agent.display_name,
                    "description": agent.description,
                    "model": agent.model,
                    "created_at": agent.create_time.isoformat() if hasattr(agent, 'create_time') else None,
                    "updated_at": agent.update_time.isoformat() if hasattr(agent, 'update_time') else None,
                    "status": "active"
                })
            
            return agent_list
            
        except Exception as e:
            logging.error(f"Failed to list agents: {str(e)}")
            raise
    
    def execute_agent(self, 
                     agent_id: str, 
                     query: str, 
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an agent with a query.
        
        Args:
            agent_id: ID of the agent to execute
            query: User query to process
            context: Additional context for the agent (optional)
            
        Returns:
            Dict containing the agent response and metadata
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        try:
            agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            agent = Agent(agent_name)
            
            # Create agent context if provided
            agent_context = None
            if context:
                agent_context = AgentContext(context=context)
            
            # Execute the agent
            response = agent.query(
                query=query,
                context=agent_context
            )
            
            # Extract response details
            result = {
                "response": response.text,
                "metadata": {
                    "tool_calls": [],
                    "citations": []
                }
            }
            
            # Extract tool calls if available
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    result["metadata"]["tool_calls"].append({
                        "tool_name": tool_call.name,
                        "input": tool_call.input,
                        "output": tool_call.output
                    })
            
            # Extract citations if available
            if hasattr(response, 'citations') and response.citations:
                for citation in response.citations:
                    result["metadata"]["citations"].append({
                        "start_index": citation.start_index,
                        "end_index": citation.end_index,
                        "url": citation.url if hasattr(citation, 'url') else None,
                        "title": citation.title if hasattr(citation, 'title') else None,
                        "license": citation.license if hasattr(citation, 'license') else None
                    })
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to execute agent {agent_id}: {str(e)}")
            raise
    
    def deploy_agent(self, agent_id: str) -> Dict[str, Any]:
        """Deploy an agent to make it available for serving.
        
        Args:
            agent_id: ID of the agent to deploy
            
        Returns:
            Dict containing deployment status
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        try:
            agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            agent = Agent(agent_name)
            
            # Deploy the agent
            # Note: In ADK, agents are automatically deployed when created
            # This method is provided for consistency with the framework
            
            return {
                "status": "deployed",
                "message": "Agent is ready for serving",
                "agent_id": agent_id,
                "endpoint": f"https://{self.location}-aiplatform.googleapis.com/v1/{agent_name}:query"
            }
            
        except Exception as e:
            logging.error(f"Failed to deploy agent {agent_id}: {str(e)}")
            return {
                "status": "failed",
                "message": f"Deployment failed: {str(e)}",
                "agent_id": agent_id
            }
    
    def get_deployment_status(self, agent_id: str) -> Dict[str, Any]:
        """Get the deployment status of an agent.
        
        Args:
            agent_id: ID of the agent to check
            
        Returns:
            Dict containing deployment status
        """
        if not self.initialized:
            raise RuntimeError("ADK integration not initialized")
        
        try:
            agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            agent = Agent(agent_name)
            
            # Check if agent exists and is accessible
            _ = agent.display_name
            
            return {
                "status": "deployed",
                "message": "Agent is ready for serving",
                "agent_id": agent_id,
                "endpoint": f"https://{self.location}-aiplatform.googleapis.com/v1/{agent_name}:query"
            }
            
        except Exception as e:
            logging.error(f"Failed to get deployment status for agent {agent_id}: {str(e)}")
            return {
                "status": "unknown",
                "message": f"Failed to determine status: {str(e)}",
                "agent_id": agent_id
            }
