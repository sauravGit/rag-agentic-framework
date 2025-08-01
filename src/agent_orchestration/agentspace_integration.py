"""
Google Agentspace integration module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides integration with Google's Agentspace for discovering, sharing,
and governing AI agents across an organization.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

# Import Agentspace components
try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform.agentspace import AgentspaceClient
    from google.cloud.aiplatform.agentspace import Agent, AgentGallery, AgentDesigner
    from google.cloud.aiplatform.agentspace import AgentPolicy, AgentPermission
except ImportError:
    logging.warning("Google Cloud AI Platform SDK not installed. Agentspace integration will not be available.")

# Local imports
from ..core.config import Config

class AgentspaceIntegration:
    """Integration with Google's Agentspace platform."""
    
    def __init__(self, config: Config):
        """Initialize the Agentspace integration.
        
        Args:
            config: Configuration object containing Agentspace settings
        """
        self.config = config
        self.project_id = config.get("gcp.project_id")
        self.location = config.get("gcp.location", "us-central1")
        self.agentspace_client = None
        self.initialized = False
        
        # Initialize Agentspace if available
        if "google.cloud.aiplatform.agentspace" in globals():
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                self.agentspace_client = AgentspaceClient()
                self.initialized = True
                logging.info(f"Agentspace integration initialized for project {self.project_id} in {self.location}")
            except Exception as e:
                logging.error(f"Failed to initialize Agentspace: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Agentspace integration is available.
        
        Returns:
            bool: True if Agentspace is available, False otherwise
        """
        return self.initialized
    
    def publish_agent(self, 
                     agent_id: str,
                     gallery_id: str = None,
                     visibility: str = "private",
                     description: str = None,
                     tags: List[str] = None) -> Dict[str, Any]:
        """Publish an agent to Agentspace.
        
        Args:
            agent_id: ID of the agent to publish
            gallery_id: ID of the gallery to publish to (optional)
            visibility: Visibility level ('private', 'organization', 'public')
            description: Updated description for the published agent (optional)
            tags: List of tags for the agent (optional)
            
        Returns:
            Dict containing the published agent details
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        try:
            # Get the agent from Vertex AI
            agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            
            # Prepare publication details
            publication_details = {
                "visibility": visibility
            }
            
            if description:
                publication_details["description"] = description
                
            if tags:
                publication_details["tags"] = tags
            
            # Publish to specified gallery or default gallery
            gallery_path = None
            if gallery_id:
                gallery_path = f"projects/{self.project_id}/locations/{self.location}/agentGalleries/{gallery_id}"
            
            # Publish the agent
            published_agent = self.agentspace_client.publish_agent(
                agent=agent_name,
                gallery=gallery_path,
                publication_details=publication_details
            )
            
            # Return published agent details
            return {
                "id": published_agent.name.split("/")[-1],
                "agent_id": agent_id,
                "gallery_id": gallery_id or "default",
                "visibility": visibility,
                "description": description or "",
                "tags": tags or [],
                "status": "published",
                "published_at": published_agent.create_time.isoformat() if hasattr(published_agent, 'create_time') else None
            }
            
        except Exception as e:
            logging.error(f"Failed to publish agent {agent_id}: {str(e)}")
            raise
    
    def unpublish_agent(self, published_agent_id: str, gallery_id: str = None) -> bool:
        """Unpublish an agent from Agentspace.
        
        Args:
            published_agent_id: ID of the published agent to unpublish
            gallery_id: ID of the gallery the agent is published to (optional)
            
        Returns:
            bool: True if unpublishing was successful
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        try:
            # Construct the published agent path
            gallery_path = None
            if gallery_id:
                gallery_path = f"projects/{self.project_id}/locations/{self.location}/agentGalleries/{gallery_id}"
                
            published_agent_path = f"projects/{self.project_id}/locations/{self.location}/publishedAgents/{published_agent_id}"
            
            # Unpublish the agent
            self.agentspace_client.unpublish_agent(
                published_agent=published_agent_path,
                gallery=gallery_path
            )
            
            logging.info(f"Unpublished agent: {published_agent_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to unpublish agent {published_agent_id}: {str(e)}")
            raise
    
    def list_published_agents(self, gallery_id: str = None) -> List[Dict[str, Any]]:
        """List published agents in Agentspace.
        
        Args:
            gallery_id: ID of the gallery to list agents from (optional)
            
        Returns:
            List of dicts containing published agent details
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        try:
            # Construct the gallery path
            gallery_path = None
            if gallery_id:
                gallery_path = f"projects/{self.project_id}/locations/{self.location}/agentGalleries/{gallery_id}"
            
            # List published agents
            published_agents = self.agentspace_client.list_published_agents(
                gallery=gallery_path
            )
            
            # Convert to list of dicts
            agent_list = []
            for agent in published_agents:
                agent_id = agent.name.split("/")[-1]
                agent_list.append({
                    "id": agent_id,
                    "name": agent.display_name,
                    "display_name": agent.display_name,
                    "description": agent.description,
                    "visibility": agent.visibility,
                    "tags": agent.tags if hasattr(agent, 'tags') else [],
                    "published_at": agent.create_time.isoformat() if hasattr(agent, 'create_time') else None,
                    "updated_at": agent.update_time.isoformat() if hasattr(agent, 'update_time') else None,
                    "status": "published"
                })
            
            return agent_list
            
        except Exception as e:
            logging.error(f"Failed to list published agents: {str(e)}")
            raise
    
    def create_gallery(self, 
                      name: str, 
                      description: str, 
                      display_name: str = None) -> Dict[str, Any]:
        """Create a new agent gallery in Agentspace.
        
        Args:
            name: Unique name for the gallery
            description: Description of the gallery's purpose
            display_name: Human-readable display name (defaults to name if not provided)
            
        Returns:
            Dict containing the created gallery details
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        display_name = display_name or name
        
        try:
            # Create the gallery
            gallery = self.agentspace_client.create_agent_gallery(
                display_name=display_name,
                description=description
            )
            
            # Return gallery details
            gallery_details = {
                "id": gallery.name.split("/")[-1],
                "name": name,
                "display_name": display_name,
                "description": description,
                "created_at": gallery.create_time.isoformat() if hasattr(gallery, 'create_time') else None,
                "updated_at": gallery.update_time.isoformat() if hasattr(gallery, 'update_time') else None,
                "status": "active"
            }
            
            logging.info(f"Created gallery: {gallery_details['id']}")
            return gallery_details
            
        except Exception as e:
            logging.error(f"Failed to create gallery: {str(e)}")
            raise
    
    def delete_gallery(self, gallery_id: str) -> bool:
        """Delete an agent gallery from Agentspace.
        
        Args:
            gallery_id: ID of the gallery to delete
            
        Returns:
            bool: True if deletion was successful
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        try:
            gallery_path = f"projects/{self.project_id}/locations/{self.location}/agentGalleries/{gallery_id}"
            
            # Delete the gallery
            self.agentspace_client.delete_agent_gallery(
                name=gallery_path
            )
            
            logging.info(f"Deleted gallery: {gallery_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete gallery {gallery_id}: {str(e)}")
            raise
    
    def list_galleries(self) -> List[Dict[str, Any]]:
        """List all agent galleries in Agentspace.
        
        Returns:
            List of dicts containing gallery details
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        try:
            # List galleries
            galleries = self.agentspace_client.list_agent_galleries(
                parent=f"projects/{self.project_id}/locations/{self.location}"
            )
            
            # Convert to list of dicts
            gallery_list = []
            for gallery in galleries:
                gallery_id = gallery.name.split("/")[-1]
                gallery_list.append({
                    "id": gallery_id,
                    "name": gallery.display_name,
                    "display_name": gallery.display_name,
                    "description": gallery.description,
                    "created_at": gallery.create_time.isoformat() if hasattr(gallery, 'create_time') else None,
                    "updated_at": gallery.update_time.isoformat() if hasattr(gallery, 'update_time') else None,
                    "status": "active"
                })
            
            return gallery_list
            
        except Exception as e:
            logging.error(f"Failed to list galleries: {str(e)}")
            raise
    
    def set_agent_permissions(self, 
                             published_agent_id: str, 
                             permissions: List[Dict[str, Any]]) -> bool:
        """Set permissions for a published agent.
        
        Args:
            published_agent_id: ID of the published agent
            permissions: List of permission objects with 'principal' and 'role' keys
            
        Returns:
            bool: True if permissions were set successfully
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        try:
            published_agent_path = f"projects/{self.project_id}/locations/{self.location}/publishedAgents/{published_agent_id}"
            
            # Convert permission dicts to AgentPermission objects
            agent_permissions = []
            for perm in permissions:
                agent_permission = AgentPermission(
                    principal=perm.get("principal"),
                    role=perm.get("role")
                )
                agent_permissions.append(agent_permission)
            
            # Set permissions
            self.agentspace_client.set_agent_permissions(
                published_agent=published_agent_path,
                permissions=agent_permissions
            )
            
            logging.info(f"Set permissions for published agent: {published_agent_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to set permissions for published agent {published_agent_id}: {str(e)}")
            raise
    
    def get_agent_permissions(self, published_agent_id: str) -> List[Dict[str, Any]]:
        """Get permissions for a published agent.
        
        Args:
            published_agent_id: ID of the published agent
            
        Returns:
            List of permission objects with 'principal' and 'role' keys
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        try:
            published_agent_path = f"projects/{self.project_id}/locations/{self.location}/publishedAgents/{published_agent_id}"
            
            # Get permissions
            permissions = self.agentspace_client.get_agent_permissions(
                published_agent=published_agent_path
            )
            
            # Convert to list of dicts
            permission_list = []
            for perm in permissions:
                permission_list.append({
                    "principal": perm.principal,
                    "role": perm.role
                })
            
            return permission_list
            
        except Exception as e:
            logging.error(f"Failed to get permissions for published agent {published_agent_id}: {str(e)}")
            raise
    
    def create_agent_with_designer(self, 
                                 name: str, 
                                 description: str,
                                 display_name: str = None,
                                 template: str = "medical_assistant") -> Dict[str, Any]:
        """Create a new agent using the no-code Agent Designer.
        
        Args:
            name: Unique name for the agent
            description: Description of the agent's purpose
            display_name: Human-readable display name (defaults to name if not provided)
            template: Template to use for the agent
            
        Returns:
            Dict containing the created agent details
        """
        if not self.initialized:
            raise RuntimeError("Agentspace integration not initialized")
        
        display_name = display_name or name
        
        try:
            # Create the agent using Agent Designer
            designer = AgentDesigner()
            
            agent = designer.create_agent(
                display_name=display_name,
                description=description,
                template=template
            )
            
            # Return agent details
            agent_details = {
                "id": agent.name.split("/")[-1],
                "name": name,
                "display_name": display_name,
                "description": description,
                "template": template,
                "created_at": agent.create_time.isoformat() if hasattr(agent, 'create_time') else None,
                "updated_at": agent.update_time.isoformat() if hasattr(agent, 'update_time') else None,
                "status": "created"
            }
            
            logging.info(f"Created agent with Designer: {agent_details['id']}")
            return agent_details
            
        except Exception as e:
            logging.error(f"Failed to create agent with Designer: {str(e)}")
            raise
