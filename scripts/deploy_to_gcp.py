"""
Deployment script for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This script automates the deployment of the framework to Google Cloud Platform.
"""

import os
import argparse
import subprocess
import json
import yaml
import time
from typing import Dict, Any, List, Optional

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Deploy Enhanced MLOps Framework for Agentic AI RAG Workflows to GCP')
    
    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--region', default='us-central1', help='GCP Region')
    parser.add_argument('--config', default='config/medical_rag_config.yaml', help='Path to configuration file')
    parser.add_argument('--service-account', help='Service account email (will create one if not provided)')
    parser.add_argument('--enable-apis', action='store_true', help='Enable required GCP APIs')
    parser.add_argument('--setup-network', action='store_true', help='Setup VPC network')
    parser.add_argument('--deploy-all', action='store_true', help='Deploy all components')
    parser.add_argument('--deploy-api-gateway', action='store_true', help='Deploy API Gateway')
    parser.add_argument('--deploy-agent-orchestrator', action='store_true', help='Deploy Agent Orchestrator')
    parser.add_argument('--deploy-document-processor', action='store_true', help='Deploy Document Processor')
    parser.add_argument('--deploy-compliance-service', action='store_true', help='Deploy Compliance Service')
    parser.add_argument('--deploy-evaluation-service', action='store_true', help='Deploy Evaluation Service')
    parser.add_argument('--deploy-monitoring-service', action='store_true', help='Deploy Monitoring Service')
    parser.add_argument('--deploy-cost-optimizer', action='store_true', help='Deploy Cost Optimizer')
    parser.add_argument('--deploy-web-ui', action='store_true', help='Deploy Web UI')
    parser.add_argument('--dry-run', action='store_true', help='Print commands without executing')
    
    return parser.parse_args()

def run_command(cmd: List[str], dry_run: bool = False) -> str:
    """Run a shell command and return the output.
    
    Args:
        cmd: Command to run as a list of strings
        dry_run: If True, print the command without executing
        
    Returns:
        Command output as string
    """
    cmd_str = ' '.join(cmd)
    print(f"Running: {cmd_str}")
    
    if dry_run:
        return "DRY RUN - Command not executed"
    
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        raise

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Configuration as dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration from {config_path}: {str(e)}")
        raise

def enable_apis(project_id: str, apis: List[str], dry_run: bool = False) -> None:
    """Enable required GCP APIs.
    
    Args:
        project_id: GCP Project ID
        apis: List of APIs to enable
        dry_run: If True, print commands without executing
    """
    print(f"Enabling APIs for project {project_id}...")
    
    for api in apis:
        cmd = ['gcloud', 'services', 'enable', api, '--project', project_id]
        run_command(cmd, dry_run)
    
    print("APIs enabled successfully")

def setup_service_account(project_id: str, name: str, roles: List[str], dry_run: bool = False) -> str:
    """Setup service account with required roles.
    
    Args:
        project_id: GCP Project ID
        name: Service account name
        roles: List of roles to assign
        dry_run: If True, print commands without executing
        
    Returns:
        Service account email
    """
    print(f"Setting up service account {name} for project {project_id}...")
    
    # Create service account
    cmd = [
        'gcloud', 'iam', 'service-accounts', 'create', name,
        '--display-name', f"Service account for Enhanced MLOps Framework",
        '--project', project_id
    ]
    run_command(cmd, dry_run)
    
    # Get service account email
    sa_email = f"{name}@{project_id}.iam.gserviceaccount.com"
    
    # Assign roles
    for role in roles:
        cmd = [
            'gcloud', 'projects', 'add-iam-policy-binding', project_id,
            '--member', f"serviceAccount:{sa_email}",
            '--role', role
        ]
        run_command(cmd, dry_run)
    
    print(f"Service account {sa_email} created and configured successfully")
    return sa_email

def setup_network(project_id: str, region: str, dry_run: bool = False) -> Dict[str, str]:
    """Setup VPC network for the deployment.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        dry_run: If True, print commands without executing
        
    Returns:
        Dictionary with network and subnet names
    """
    print(f"Setting up network for project {project_id} in region {region}...")
    
    network_name = "rag-network"
    subnet_name = "rag-subnet"
    
    # Create VPC network
    cmd = [
        'gcloud', 'compute', 'networks', 'create', network_name,
        '--subnet-mode', 'custom',
        '--project', project_id
    ]
    run_command(cmd, dry_run)
    
    # Create subnet
    cmd = [
        'gcloud', 'compute', 'networks', 'subnets', 'create', subnet_name,
        '--network', network_name,
        '--region', region,
        '--range', '10.0.0.0/20',
        '--project', project_id
    ]
    run_command(cmd, dry_run)
    
    # Create firewall rule for internal communication
    cmd = [
        'gcloud', 'compute', 'firewall-rules', 'create', f"{network_name}-allow-internal",
        '--network', network_name,
        '--allow', 'tcp,udp,icmp',
        '--source-ranges', '10.0.0.0/20',
        '--project', project_id
    ]
    run_command(cmd, dry_run)
    
    # Create firewall rule for health checks
    cmd = [
        'gcloud', 'compute', 'firewall-rules', 'create', f"{network_name}-allow-health-checks",
        '--network', network_name,
        '--allow', 'tcp',
        '--source-ranges', '130.211.0.0/22,35.191.0.0/16',
        '--project', project_id
    ]
    run_command(cmd, dry_run)
    
    print(f"Network {network_name} and subnet {subnet_name} created successfully")
    return {
        "network": network_name,
        "subnet": subnet_name
    }

def deploy_cloud_run_service(
    project_id: str,
    region: str,
    service_name: str,
    image: str,
    sa_email: str,
    env_vars: Dict[str, str] = None,
    memory: str = "1Gi",
    cpu: str = "1",
    min_instances: int = 0,
    max_instances: int = 10,
    dry_run: bool = False
) -> str:
    """Deploy a service to Cloud Run.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        service_name: Service name
        image: Container image
        sa_email: Service account email
        env_vars: Environment variables
        memory: Memory allocation
        cpu: CPU allocation
        min_instances: Minimum instances
        max_instances: Maximum instances
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    print(f"Deploying {service_name} to Cloud Run in project {project_id}, region {region}...")
    
    # Build command
    cmd = [
        'gcloud', 'run', 'deploy', service_name,
        '--image', image,
        '--platform', 'managed',
        '--region', region,
        '--service-account', sa_email,
        '--memory', memory,
        '--cpu', cpu,
        '--min-instances', str(min_instances),
        '--max-instances', str(max_instances),
        '--project', project_id
    ]
    
    # Add environment variables
    if env_vars:
        env_list = [f"{k}={v}" for k, v in env_vars.items()]
        env_str = ','.join(env_list)
        cmd.extend(['--set-env-vars', env_str])
    
    # Run command
    output = run_command(cmd, dry_run)
    
    # Extract service URL
    service_url = None
    if not dry_run:
        for line in output.splitlines():
            if "Service URL:" in line:
                service_url = line.split("Service URL:")[1].strip()
                break
    
    print(f"{service_name} deployed successfully")
    return service_url

def deploy_api_gateway(
    project_id: str,
    region: str,
    sa_email: str,
    config: Dict[str, Any],
    network_info: Dict[str, str],
    dry_run: bool = False
) -> str:
    """Deploy API Gateway service.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        config: Configuration dictionary
        network_info: Network information
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "api-gateway"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/api-gateway:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/api-gateway'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "CONFIG_PATH": "/app/config/medical_rag_config.yaml",
        "LOG_LEVEL": "INFO",
        "PROJECT_ID": project_id,
        "REGION": region
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="2Gi",
        cpu="2",
        min_instances=1,
        max_instances=10,
        dry_run=dry_run
    )

def deploy_agent_orchestrator(
    project_id: str,
    region: str,
    sa_email: str,
    config: Dict[str, Any],
    network_info: Dict[str, str],
    dry_run: bool = False
) -> str:
    """Deploy Agent Orchestrator service.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        config: Configuration dictionary
        network_info: Network information
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "agent-orchestrator"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/agent-orchestrator:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/agent-orchestrator'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "CONFIG_PATH": "/app/config/medical_rag_config.yaml",
        "LOG_LEVEL": "INFO",
        "PROJECT_ID": project_id,
        "REGION": region
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="2Gi",
        cpu="2",
        min_instances=1,
        max_instances=5,
        dry_run=dry_run
    )

def deploy_document_processor(
    project_id: str,
    region: str,
    sa_email: str,
    config: Dict[str, Any],
    network_info: Dict[str, str],
    dry_run: bool = False
) -> str:
    """Deploy Document Processor service.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        config: Configuration dictionary
        network_info: Network information
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "document-processor"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/document-processor:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/document-processor'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "CONFIG_PATH": "/app/config/medical_rag_config.yaml",
        "LOG_LEVEL": "INFO",
        "PROJECT_ID": project_id,
        "REGION": region
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="4Gi",
        cpu="2",
        min_instances=1,
        max_instances=5,
        dry_run=dry_run
    )

def deploy_compliance_service(
    project_id: str,
    region: str,
    sa_email: str,
    config: Dict[str, Any],
    network_info: Dict[str, str],
    dry_run: bool = False
) -> str:
    """Deploy Compliance Service.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        config: Configuration dictionary
        network_info: Network information
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "compliance-service"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/compliance-service:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/compliance-service'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "CONFIG_PATH": "/app/config/medical_rag_config.yaml",
        "LOG_LEVEL": "INFO",
        "PROJECT_ID": project_id,
        "REGION": region
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="2Gi",
        cpu="1",
        min_instances=1,
        max_instances=5,
        dry_run=dry_run
    )

def deploy_evaluation_service(
    project_id: str,
    region: str,
    sa_email: str,
    config: Dict[str, Any],
    network_info: Dict[str, str],
    dry_run: bool = False
) -> str:
    """Deploy Evaluation Service.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        config: Configuration dictionary
        network_info: Network information
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "evaluation-service"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/evaluation-service:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/evaluation-service'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "CONFIG_PATH": "/app/config/medical_rag_config.yaml",
        "LOG_LEVEL": "INFO",
        "PROJECT_ID": project_id,
        "REGION": region
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="2Gi",
        cpu="1",
        min_instances=0,
        max_instances=5,
        dry_run=dry_run
    )

def deploy_monitoring_service(
    project_id: str,
    region: str,
    sa_email: str,
    config: Dict[str, Any],
    network_info: Dict[str, str],
    dry_run: bool = False
) -> str:
    """Deploy Monitoring Service.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        config: Configuration dictionary
        network_info: Network information
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "monitoring-service"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/monitoring-service:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/monitoring-service'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "CONFIG_PATH": "/app/config/medical_rag_config.yaml",
        "LOG_LEVEL": "INFO",
        "PROJECT_ID": project_id,
        "REGION": region
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="2Gi",
        cpu="1",
        min_instances=1,
        max_instances=3,
        dry_run=dry_run
    )

def deploy_cost_optimizer(
    project_id: str,
    region: str,
    sa_email: str,
    config: Dict[str, Any],
    network_info: Dict[str, str],
    dry_run: bool = False
) -> str:
    """Deploy Cost Optimizer service.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        config: Configuration dictionary
        network_info: Network information
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "cost-optimizer"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/cost-optimizer:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/cost-optimizer'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "CONFIG_PATH": "/app/config/medical_rag_config.yaml",
        "LOG_LEVEL": "INFO",
        "PROJECT_ID": project_id,
        "REGION": region
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="1Gi",
        cpu="1",
        min_instances=0,
        max_instances=2,
        dry_run=dry_run
    )

def deploy_web_ui(
    project_id: str,
    region: str,
    sa_email: str,
    api_url: str,
    monitoring_url: str,
    dry_run: bool = False
) -> str:
    """Deploy Web UI.
    
    Args:
        project_id: GCP Project ID
        region: GCP Region
        sa_email: Service account email
        api_url: API Gateway URL
        monitoring_url: Monitoring Service URL
        dry_run: If True, print commands without executing
        
    Returns:
        Service URL
    """
    service_name = "web-ui"
    image = f"gcr.io/{project_id}/enhanced-rag-framework/web-ui:latest"
    
    # Build and push container image
    cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', image,
        '--project', project_id,
        'docker/web-ui'
    ]
    run_command(cmd, dry_run)
    
    # Deploy to Cloud Run
    env_vars = {
        "REACT_APP_API_URL": api_url,
        "REACT_APP_MONITORING_URL": monitoring_url
    }
    
    return deploy_cloud_run_service(
        project_id=project_id,
        region=region,
        service_name=service_name,
        image=image,
        sa_email=sa_email,
        env_vars=env_vars,
        memory="1Gi",
        cpu="1",
        min_instances=1,
        max_instances=3,
        dry_run=dry_run
    )

def main():
    """Main function."""
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Update configuration with command line arguments
    config['gcp'] = config.get('gcp', {})
    config['gcp']['project_id'] = args.project_id
    config['gcp']['location'] = args.region
    
    # Enable APIs if requested
    if args.enable_apis:
        apis = config.get('gcp', {}).get('enable_apis', [
            'aiplatform.googleapis.com',
            'documentai.googleapis.com',
            'storage.googleapis.com',
            'logging.googleapis.com',
            'monitoring.googleapis.com',
            'run.googleapis.com',
            'cloudbuild.googleapis.com',
            'artifactregistry.googleapis.com',
            'compute.googleapis.com'
        ])
        enable_apis(args.project_id, apis, args.dry_run)
    
    # Setup service account if not provided
    sa_email = args.service_account
    if not sa_email:
        sa_name = "rag-framework-sa"
        roles = [
            'roles/aiplatform.user',
            'roles/storage.admin',
            'roles/logging.admin',
            'roles/monitoring.admin',
            'roles/run.admin',
            'roles/cloudbuild.builds.builder',
            'roles/artifactregistry.admin',
            'roles/documentai.admin'
        ]
        sa_email = setup_service_account(args.project_id, sa_name, roles, args.dry_run)
    
    # Setup network if requested
    network_info = None
    if args.setup_network:
        network_info = setup_network(args.project_id, args.region, args.dry_run)
    
    # Deploy services
    service_urls = {}
    
    if args.deploy_all or args.deploy_api_gateway:
        service_urls['api_gateway'] = deploy_api_gateway(
            args.project_id, args.region, sa_email, config, network_info, args.dry_run
        )
    
    if args.deploy_all or args.deploy_agent_orchestrator:
        service_urls['agent_orchestrator'] = deploy_agent_orchestrator(
            args.project_id, args.region, sa_email, config, network_info, args.dry_run
        )
    
    if args.deploy_all or args.deploy_document_processor:
        service_urls['document_processor'] = deploy_document_processor(
            args.project_id, args.region, sa_email, config, network_info, args.dry_run
        )
    
    if args.deploy_all or args.deploy_compliance_service:
        service_urls['compliance_service'] = deploy_compliance_service(
            args.project_id, args.region, sa_email, config, network_info, args.dry_run
        )
    
    if args.deploy_all or args.deploy_evaluation_service:
        service_urls['evaluation_service'] = deploy_evaluation_service(
            args.project_id, args.region, sa_email, config, network_info, args.dry_run
        )
    
    if args.deploy_all or args.deploy_monitoring_service:
        service_urls['monitoring_service'] = deploy_monitoring_service(
            args.project_id, args.region, sa_email, config, network_info, args.dry_run
        )
    
    if args.deploy_all or args.deploy_cost_optimizer:
        service_urls['cost_optimizer'] = deploy_cost_optimizer(
            args.project_id, args.region, sa_email, config, network_info, args.dry_run
        )
    
    if args.deploy_all or args.deploy_web_ui:
        api_url = service_urls.get('api_gateway', '')
        monitoring_url = service_urls.get('monitoring_service', '')
        service_urls['web_ui'] = deploy_web_ui(
            args.project_id, args.region, sa_email, api_url, monitoring_url, args.dry_run
        )
    
    # Print summary
    print("\nDeployment Summary:")
    print(f"Project ID: {args.project_id}")
    print(f"Region: {args.region}")
    print(f"Service Account: {sa_email}")
    
    if service_urls:
        print("\nService URLs:")
        for service, url in service_urls.items():
            print(f"  {service}: {url}")
    
    print("\nDeployment completed successfully!")

if __name__ == "__main__":
    main()
