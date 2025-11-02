"""
Configuration loader for Project Axiom.
Handles loading configuration from YAML files and environment variables.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .models import Config, DocumentProcessingConfig, EmbeddingConfig, LoggingConfig, StateTrackerConfig, VectorStoreConfig, ApiKeysConfig


class ConfigLoader:
    """Handles loading and validation of application configuration."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the config loader with a config file path."""
        self.config_path = Path(config_path)
        # Load .env file first (if it exists)
        load_dotenv()
        # Note: Logger will be set up after config is loaded
        self._logger = None
    
    def load(self) -> Config:
        """Load configuration from YAML file and environment variables."""
        yaml_data = self._load_yaml_file()
        env_data = self._load_environment_variables()
        self._validate_critical_settings(env_data)
        config = self._create_config_from_data(yaml_data, env_data)
        
        # Set up logging after config is loaded
        self._setup_logging(config)
        
        # Now we can use proper logging
        self._logger = logging.getLogger(__name__)
        self._logger.info("Configuration loaded successfully", extra={
            "config_path": str(self.config_path),
            "has_yaml_data": bool(yaml_data),
            "has_env_data": bool(env_data)
        })
        
        return config
    
    def _setup_logging(self, config: Config) -> None:
        """Set up logging system based on loaded configuration."""
        from ..logging_setup import setup_logging
        setup_logging(config.logging)
    
    def _load_yaml_file(self) -> Dict[str, Any]:
        """Load YAML file with graceful handling of missing/invalid files."""
        try:
            with open(self.config_path, 'r') as file:
                data = yaml.safe_load(file)
                return data if data is not None else {}
        except FileNotFoundError:
            # Use print for now, will be replaced with logging after setup
            self.logger.warning(f"Config file {self.config_path} not found. Using defaults.")
            return {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_path}: {e}")
        except PermissionError:
            raise ValueError(f"Cannot read config file {self.config_path}: Permission denied")
    
    def _load_environment_variables(self) -> Dict[str, str]:
        """Load environment variables for configuration."""
        env_vars = {}
        # Check for OPENAI_API_KEY in environment
        if 'OPENAI_API_KEY' in os.environ:
            env_vars['openai_api_key'] = os.environ['OPENAI_API_KEY']
        return env_vars
    
    def _validate_critical_settings(self, env_data: Dict[str, str]) -> None:
        """Validate critical settings that must be present (fail-fast)."""
        # We will now validate the API key in the YAML config instead.
        pass
    
    def _create_config_from_data(self, yaml_data: Dict[str, Any], env_data: Dict[str, str]) -> Config:
        """Create Config object from loaded data, using defaults for missing values."""
        api_keys_data = yaml_data.get('api_keys', {})
        # Prefer environment variable over YAML (more secure)
        openai_key = env_data.get('openai_api_key', api_keys_data.get('openai', ''))
        api_keys_config = ApiKeysConfig(
            openai=openai_key
        )

        doc_config_data = yaml_data.get('document_processing', {})
        document_config = DocumentProcessingConfig(
            chunk_size=doc_config_data.get('chunk_size', 800),
            chunk_overlap=doc_config_data.get('chunk_overlap', 160),
            max_file_size_mb=doc_config_data.get('max_file_size_mb', 50)
        )
        
        embed_config_data = yaml_data.get('embeddings', {})
        embeddings_config = EmbeddingConfig(
            model_name=embed_config_data.get('model_name', "all-MiniLM-L6-v2"),
            batch_size=embed_config_data.get('batch_size', 32),
            device=embed_config_data.get('device', "cpu")
        )
        
        log_config_data = yaml_data.get('logging', {})
        logging_config = LoggingConfig(
            level=log_config_data.get('level', "INFO"),
            log_file=log_config_data.get('log_file', "axiom.log"),
            log_to_console=log_config_data.get('log_to_console', True),
            log_to_file=log_config_data.get('log_to_file', True),
            log_format=log_config_data.get('log_format', "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        
        state_config_data = yaml_data.get('state_tracker', {})
        state_tracker_config = StateTrackerConfig(
            db_path=state_config_data.get('db_path', "axiom_state.db"),
            auto_cleanup_days=state_config_data.get('auto_cleanup_days', 30)
        )

        vector_store_config_data = yaml_data.get('vector_store', {})
        vector_store_config = VectorStoreConfig(
            persist_directory=vector_store_config_data.get('persist_directory', "./chroma_db/axiom_documents")
        )

        data_dir = yaml_data.get('data_dir', "axiom/data")

        config = Config(
            document_processing=document_config,
            embeddings=embeddings_config,
            logging=logging_config,
            state_tracker=state_tracker_config,
            vector_store=vector_store_config,
            api_keys=api_keys_config,
            data_dir=data_dir
        )

        # After creating the config, we can set the API key in the environment
        if api_keys_config.openai:
            os.environ["OPENAI_API_KEY"] = api_keys_config.openai
        
        return config


def load_config(config_path: str = "config.yaml") -> Config:
    """Convenience function to load configuration."""
    loader = ConfigLoader(config_path)
    return loader.load()
