import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

appconfig = boto3.client("appconfigdata")
appconfig_mgmt = boto3.client("appconfig")

APPCONFIG_APP_ID = os.environ["APPCONFIG_APP_ID"]
APPCONFIG_ENV_ID = os.environ["APPCONFIG_ENV_ID"]
APPCONFIG_PROFILE_ID = os.environ["APPCONFIG_PROFILE_ID"]
APPCONFIG_DEPLOYMENT_STRATEGY_ID = os.environ["APPCONFIG_DEPLOYMENT_STRATEGY_ID"]

def sanitize_description(desc):
    """Remove non-ASCII characters from description to avoid AWS signature errors"""
    if not desc:
        return ""
    return desc.encode('ascii', 'ignore').decode('ascii')

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")
    try:
        method = event["httpMethod"]
        logger.info(f"HTTP Method: {method}")
        
        if method == "OPTIONS":
            return response(200, {})
        
        if method == "GET":
            version = event.get("queryStringParameters", {}).get("version") if event.get("queryStringParameters") else None
            return get_config(version)
        elif method == "PUT":
            body = json.loads(event.get("body", "{}"))
            logger.info(f"PUT body received: {json.dumps(body)}")
            return update_config(body)
        elif method == "DELETE":
            version = event.get("queryStringParameters", {}).get("version") if event.get("queryStringParameters") else None
            if not version:
                return response(400, {"error": "version parameter is required"})
            return delete_version(version)
        
        return response(405, {"error": "Method not allowed"})
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return response(500, {"error": str(e)})

def get_config(version=None):
    try:
        available_versions = list_versions()
        
        if version:
            logger.info(f"Getting specific version: {version}")
            config_data = get_version_content(version)
        else:
            logger.info("Getting latest deployed configuration")
            session_token = appconfig.start_configuration_session(
                ApplicationIdentifier=APPCONFIG_APP_ID,
                EnvironmentIdentifier=APPCONFIG_ENV_ID,
                ConfigurationProfileIdentifier=APPCONFIG_PROFILE_ID
            )
            
            config_response = appconfig.get_latest_configuration(
                ConfigurationToken=session_token["InitialConfigurationToken"]
            )
            
            config_content = config_response["Configuration"].read().decode("utf-8")
            config_data = json.loads(config_content)
        
        result = {
            "current_config": config_data,
            "available_versions": available_versions,
            "requested_version": version if version else "latest"
        }
        
        logger.info(f"Returning config with {len(available_versions)} available versions")
        return response(200, result)
    except Exception as e:
        logger.error(f"Error in get_config: {str(e)}", exc_info=True)
        return response(500, {"error": str(e)})

def list_versions():
    try:
        logger.info("Listing all configuration versions")
        versions_response = appconfig_mgmt.list_hosted_configuration_versions(
            ApplicationId=APPCONFIG_APP_ID,
            ConfigurationProfileId=APPCONFIG_PROFILE_ID,
            MaxResults=50
        )
        
        versions = []
        for item in versions_response.get('Items', []):
            versions.append({
                "version": item['VersionNumber'],
                "description": item.get('Description', '')
            })
        
        versions.sort(key=lambda x: x['version'], reverse=True)
        logger.info(f"Found {len(versions)} versions")
        return versions
    except Exception as e:
        logger.error(f"Error listing versions: {str(e)}")
        return []

def get_version_content(version):
    try:
        logger.info(f"Getting content for version {version}")
        version_response = appconfig_mgmt.get_hosted_configuration_version(
            ApplicationId=APPCONFIG_APP_ID,
            ConfigurationProfileId=APPCONFIG_PROFILE_ID,
            VersionNumber=int(version)
        )
        
        content = version_response['Content'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error getting version content: {str(e)}")
        raise

def update_config(data):
    try:
        if "config" not in data:
            return response(400, {"error": "Missing 'config' field in request body"})
        
        config_data = data["config"]
        description = data.get("description", "")
        create_new_version = data.get("create_new_version", False)
        
        logger.info(f"Normalizing data with {len(config_data)} keys")
        logger.info(f"Create new version: {create_new_version}")
        
        normalized_data = {}
        for key, value in config_data.items():
            if isinstance(value, bool):
                normalized_data[key] = str(value).lower()
            elif isinstance(value, (int, float)):
                normalized_data[key] = str(value)
            else:
                normalized_data[key] = value
        
        logger.info(f"Normalized data: {json.dumps(normalized_data, ensure_ascii=False)}")
        logger.info(f"Description: {description}")
        
        config_content = json.dumps(normalized_data, indent=2, ensure_ascii=False)
        logger.info(f"Config content to save (length: {len(config_content)})")
        
        # Get current deployed version
        versions = list_versions()
        if not versions:
            logger.warning("No versions found, will create first version")
            create_new_version = True
        
        current_version = versions[0]['version'] if versions else None
        
        if create_new_version:
            # Create new version + deploy
            create_params = {
                "ApplicationId": APPCONFIG_APP_ID,
                "ConfigurationProfileId": APPCONFIG_PROFILE_ID,
                "Content": config_content.encode("utf-8"),
                "ContentType": "application/json"
            }
            
            if description:
                create_params["Description"] = sanitize_description(description)
            
            create_response = appconfig_mgmt.create_hosted_configuration_version(**create_params)
            new_version = create_response['VersionNumber']
            
            logger.info(f"New configuration version created: {new_version}")
            
            logger.info(f"Starting deployment with strategy: {APPCONFIG_DEPLOYMENT_STRATEGY_ID}")
            
            deploy_response = appconfig_mgmt.start_deployment(
                ApplicationId=APPCONFIG_APP_ID,
                EnvironmentId=APPCONFIG_ENV_ID,
                DeploymentStrategyId=APPCONFIG_DEPLOYMENT_STRATEGY_ID,
                ConfigurationProfileId=APPCONFIG_PROFILE_ID,
                ConfigurationVersion=str(new_version)
            )
            
            logger.info(f"Deployment started: {deploy_response['DeploymentNumber']}")
            
            return response(200, {
                "message": "New configuration version deployed successfully",
                "version": new_version,
                "deployment": deploy_response['DeploymentNumber']
            })
        else:
            # Update current version in-place (delete + recreate with same content)
            logger.info(f"Updating current version {current_version} in-place")
            
            # Delete current version
            appconfig_mgmt.delete_hosted_configuration_version(
                ApplicationId=APPCONFIG_APP_ID,
                ConfigurationProfileId=APPCONFIG_PROFILE_ID,
                VersionNumber=current_version
            )
            logger.info(f"Deleted version {current_version}")
            
            # Recreate with updated content
            create_params = {
                "ApplicationId": APPCONFIG_APP_ID,
                "ConfigurationProfileId": APPCONFIG_PROFILE_ID,
                "Content": config_content.encode("utf-8"),
                "ContentType": "application/json"
            }
            
            if description:
                create_params["Description"] = sanitize_description(description)
            
            create_response = appconfig_mgmt.create_hosted_configuration_version(**create_params)
            new_version = create_response['VersionNumber']
            
            logger.info(f"Recreated as version: {new_version}")
            
            # Deploy the new version
            deploy_response = appconfig_mgmt.start_deployment(
                ApplicationId=APPCONFIG_APP_ID,
                EnvironmentId=APPCONFIG_ENV_ID,
                DeploymentStrategyId=APPCONFIG_DEPLOYMENT_STRATEGY_ID,
                ConfigurationProfileId=APPCONFIG_PROFILE_ID,
                ConfigurationVersion=str(new_version)
            )
            
            logger.info(f"Deployment started: {deploy_response['DeploymentNumber']}")
            
            return response(200, {
                "message": "Configuration updated successfully",
                "version": new_version,
                "deployment": deploy_response['DeploymentNumber'],
                "updated_in_place": True
            })
    except Exception as e:
        logger.error(f"Error in update_config: {str(e)}", exc_info=True)
        return response(500, {"error": str(e)})

def delete_version(version):
    try:
        logger.info(f"Deleting version {version}")
        
        appconfig_mgmt.delete_hosted_configuration_version(
            ApplicationId=APPCONFIG_APP_ID,
            ConfigurationProfileId=APPCONFIG_PROFILE_ID,
            VersionNumber=int(version)
        )
        
        logger.info(f"Version {version} deleted successfully")
        return response(200, {"message": f"Version {version} deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting version: {str(e)}", exc_info=True)
        return response(500, {"error": str(e)})

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key"
        },
        "body": json.dumps(body, default=str, ensure_ascii=False)
    }
