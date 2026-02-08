"""
Google Cloud Secret Manager Client

A Python class for pulling and setting secrets in Google Cloud Secret Manager.
Requires: google-cloud-secret-manager library
Install with: pip install google-cloud-secret-manager
"""

import logging

from google.cloud import secretmanager
from google.cloud.secretmanager_v1 import AccessSecretVersionResponse
from google.api_core import exceptions
from typing import Optional, Dict, Any, List
import json
import os

log = logging.getLogger(__name__)


class SecretManagerClient:
    """
    A client for interacting with Google Cloud Secret Manager.

    This class provides methods to:
    - Pull (access) secret values
    - Create new secrets
    - Update existing secrets
    - Add new versions to secrets
    - Delete secrets
    - Load secrets as environment variables
    """

    def __init__(self, project_id: str):
        """
        Initialize the Secret Manager client.

        Args:
            project_id: The Google Cloud project ID
        """
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, secret_id: str, version_id: str = "latest") -> str:
        """
        Pull a secret value from Secret Manager.

        Args:
            secret_id: The ID of the secret to retrieve
            version_id: The version of the secret (default: "latest")

        Returns:
            The secret value as a string

        Raises:
            google.api_core.exceptions.NotFound: If the secret doesn't exist
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"

        try:
            response: AccessSecretVersionResponse = self.client.access_secret_version(
                request={"name": name}
            )
            payload = response.payload.data.decode("UTF-8")
            return payload
        except exceptions.NotFound:
            raise ValueError(
                f"Secret '{secret_id}' not found in project '{self.project_id}'"
            )

    def get_secret_json(
        self, secret_id: str, version_id: str = "latest"
    ) -> Dict[str, Any]:
        """
        Pull a secret value and parse it as JSON.

        Args:
            secret_id: The ID of the secret to retrieve
            version_id: The version of the secret (default: "latest")

        Returns:
            The secret value parsed as a dictionary
        """
        secret_value = self.get_secret(secret_id, version_id)
        return json.loads(secret_value)

    def create_secret(
        self, secret_id: str, labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a new secret (without setting a value yet).

        Args:
            secret_id: The ID for the new secret
            labels: Optional labels to attach to the secret

        Returns:
            The resource name of the created secret
        """
        parent = f"projects/{self.project_id}"

        secret = {"replication": {"automatic": {}}}

        if labels:
            secret["labels"] = labels

        try:
            response = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": secret,
                }
            )
            return response.name
        except exceptions.AlreadyExists:
            raise ValueError(
                f"Secret '{secret_id}' already exists in project '{self.project_id}'"
            )

    def set_secret(
        self, secret_id: str, secret_value: str, create_if_missing: bool = True
    ) -> str:
        """
        Set a secret value. Creates the secret if it doesn't exist.

        Args:
            secret_id: The ID of the secret
            secret_value: The value to set
            create_if_missing: Whether to create the secret if it doesn't exist (default: True)

        Returns:
            The resource name of the secret version
        """
        # Check if secret exists, create if needed
        if create_if_missing:
            try:
                self.create_secret(secret_id)
            except ValueError:
                # Secret already exists, which is fine
                pass

        # Add a new version with the secret value
        return self.add_secret_version(secret_id, secret_value)

    def set_secret_json(
        self,
        secret_id: str,
        secret_value: Dict[str, Any],
        create_if_missing: bool = True,
    ) -> str:
        """
        Set a secret value from a dictionary (converts to JSON).

        Args:
            secret_id: The ID of the secret
            secret_value: The dictionary value to set
            create_if_missing: Whether to create the secret if it doesn't exist (default: True)

        Returns:
            The resource name of the secret version
        """
        json_value = json.dumps(secret_value)
        return self.set_secret(secret_id, json_value, create_if_missing)

    def add_secret_version(self, secret_id: str, secret_value: str) -> str:
        """
        Add a new version to an existing secret.

        Args:
            secret_id: The ID of the secret
            secret_value: The new value to add

        Returns:
            The resource name of the new secret version
        """
        parent = f"projects/{self.project_id}/secrets/{secret_id}"
        payload = secret_value.encode("UTF-8")

        try:
            response = self.client.add_secret_version(
                request={"parent": parent, "payload": {"data": payload}}
            )
            return response.name
        except exceptions.NotFound:
            raise ValueError(
                f"Secret '{secret_id}' not found. Create it first using create_secret()"
            )

    def delete_secret(self, secret_id: str) -> None:
        """
        Delete a secret and all of its versions.

        Args:
            secret_id: The ID of the secret to delete
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}"

        try:
            self.client.delete_secret(request={"name": name})
        except exceptions.NotFound:
            raise ValueError(
                f"Secret '{secret_id}' not found in project '{self.project_id}'"
            )

    def list_secrets(self) -> list:
        """
        List all secrets in the project.

        Returns:
            A list of secret resource names
        """
        parent = f"projects/{self.project_id}"
        secrets = []

        for secret in self.client.list_secrets(request={"parent": parent}):
            secrets.append(secret.name)

        return secrets

    def load_secret_to_env(
        self,
        secret_id: str,
        version_id: str = "latest",
        prefix: str = "",
        uppercase: bool = True,
        overwrite: bool = False,
    ) -> Dict[str, str]:
        """
        Load a JSON secret and set its keys as environment variables.

        Args:
            secret_id: The ID of the secret to retrieve
            version_id: The version of the secret (default: "latest")
            prefix: Optional prefix to add to all environment variable names
            uppercase: Whether to convert variable names to uppercase (default: True)
            overwrite: Whether to overwrite existing environment variables (default: False)

        Returns:
            A dictionary of the environment variables that were set

        Raises:
            ValueError: If the secret is not valid JSON
            TypeError: If the secret JSON contains non-string values

        Example:
            # If secret contains: {"database_url": "postgres://...", "api_key": "abc123"}
            # This will set: DATABASE_URL and API_KEY as environment variables
            client.load_secret_to_env("app-config")

            # With prefix:
            client.load_secret_to_env("app-config", prefix="APP_")
            # Sets: APP_DATABASE_URL and APP_API_KEY
        """
        try:
            secret_data = self.get_secret_json(secret_id, version_id)
        except json.JSONDecodeError as e:
            raise ValueError(f"Secret '{secret_id}' does not contain valid JSON: {e}")

        if not isinstance(secret_data, dict):
            raise ValueError(
                f"Secret '{secret_id}' must be a JSON object (dictionary), got {type(secret_data)}"
            )

        loaded_vars = {}

        for key, value in secret_data.items():
            # Convert value to string
            if isinstance(value, (dict, list)):
                # For complex types, convert to JSON string
                str_value = json.dumps(value)
            elif value is None:
                str_value = ""
            else:
                str_value = str(value)

            # Format the environment variable name
            env_var_name = f"{prefix}{key}"
            if uppercase:
                env_var_name = env_var_name.upper()

            # Check if variable already exists
            if env_var_name in os.environ and not overwrite:
                log.warning(
                    f"Warning: Environment variable '{env_var_name}' already exists. Skipping. "
                    f"Use overwrite=True to replace existing values."
                )
                continue

            # Set the environment variable
            os.environ[env_var_name] = str_value
            loaded_vars[env_var_name] = str_value

        return loaded_vars

    def load_multiple_secrets_to_env(
        self,
        secret_ids: List[str],
        version_id: str = "latest",
        prefix: str = "",
        uppercase: bool = True,
        overwrite: bool = False,
    ) -> Dict[str, str]:
        """
        Load multiple JSON secrets and set their keys as environment variables.

        Args:
            secret_ids: List of secret IDs to retrieve
            version_id: The version of the secrets (default: "latest")
            prefix: Optional prefix to add to all environment variable names
            uppercase: Whether to convert variable names to uppercase (default: True)
            overwrite: Whether to overwrite existing environment variables (default: False)

        Returns:
            A dictionary of all environment variables that were set

        Example:
            client.load_multiple_secrets_to_env(["app-config", "database-config", "api-keys"])
        """
        all_loaded_vars = {}

        for secret_id in secret_ids:
            try:
                loaded_vars = self.load_secret_to_env(
                    secret_id=secret_id,
                    version_id=version_id,
                    prefix=prefix,
                    uppercase=uppercase,
                    overwrite=overwrite,
                )
                all_loaded_vars.update(loaded_vars)
            except Exception as e:
                log.error(f"Error loading secret '{secret_id}': {e}")

        return all_loaded_vars


# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = SecretManagerClient(project_id="your-project-id")

    # Create and set a secret
    client.set_secret("my-api-key", "super-secret-value")

    # Pull a secret
    api_key = client.get_secret("my-api-key")
    print(f"API Key: {api_key}")

    # Set a JSON secret
    config = {
        "database_url": "postgresql://localhost/mydb",
        "api_endpoint": "https://api.example.com",
        "max_connections": 100,
        "debug_mode": True,
    }
    client.set_secret_json("app-config", config)

    # Pull a JSON secret
    retrieved_config = client.get_secret_json("app-config")
    print(f"Config: {retrieved_config}")

    # Load JSON secret as environment variables
    print("\nLoading secrets to environment variables...")
    loaded_vars = client.load_secret_to_env("app-config", prefix="APP_")
    print(f"Loaded {len(loaded_vars)} environment variables:")
    for var_name in loaded_vars:
        print(f"  - {var_name}")

    # Access the environment variables
    print(f"\nAccessing environment variables:")
    print(f"DATABASE_URL: {os.getenv('APP_DATABASE_URL')}")
    print(f"API_ENDPOINT: {os.getenv('APP_API_ENDPOINT')}")
    print(f"MAX_CONNECTIONS: {os.getenv('APP_MAX_CONNECTIONS')}")

    # Load multiple secrets at once
    print("\nLoading multiple secrets...")
    all_vars = client.load_multiple_secrets_to_env(
        secret_ids=["app-config", "database-config"], prefix="PROD_"
    )
    print(f"Loaded {len(all_vars)} total environment variables")

    # List all secrets
    all_secrets = client.list_secrets()
    print(f"\nAll secrets: {all_secrets}")
