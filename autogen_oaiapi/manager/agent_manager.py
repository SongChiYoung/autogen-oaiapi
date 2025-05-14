import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self, agents_dir: str, config_list: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the AgentManager.
        
        Args:
            agents_dir: Directory containing agent JSON files
            config_list: Optional list of configurations for AutoGen agents
        """
        self.agents_dir = Path(agents_dir).resolve()  # Get absolute path
        self.config_list = config_list
        self.agents: Dict[str, Dict[str, Any]] = {}
        
        # Create agents directory if it doesn't exist
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized AgentManager with agents directory: {self.agents_dir}")
    
    def _validate_agent_data(self, agent_data: Dict[str, Any], file_path: Path) -> bool:
        """Validate that the agent data contains all required fields."""
        required_fields = ['provider', 'component_type', 'version', 'description', 'label']
        missing_fields = [field for field in required_fields if field not in agent_data]
        
        if missing_fields:
            logger.error(f"Agent file {file_path} is missing required fields: {missing_fields}")
            return False
        
        return True
    
    def load_agents(self) -> None:
        """Load all JSON files from the agents directory and initialize team configurations."""
        self.agents.clear()
        
        logger.info(f"Searching for JSON files in: {self.agents_dir}")
        json_files = list(self.agents_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files")
        
        for json_file in json_files:
            try:
                logger.info(f"Processing JSON file: {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                if not self._validate_agent_data(agent_data, json_file):
                    continue
                
                # Store the agent configuration
                self.agents[str(json_file.stem)] = {
                    'team_config': agent_data,
                    'file_path': str(json_file)
                }
                logger.info(f"Stored team configuration for: {json_file.stem}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON file {json_file}: {str(e)}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {str(e)}")
        
        logger.info(f"Finished loading agents. Total agents loaded: {len(self.agents)}")
        logger.info(f"Available agents: {list(self.agents.keys())}")
        
        if not self.agents:
            logger.warning("No agents were loaded successfully!")
    
    def get_agent(self, agent_path: str) -> Optional[Dict[str, Any]]:
        """Get an agent configuration by path."""
        return self.agents.get(agent_path)
    
    def list_agents(self) -> List[str]:
        """List all available agent paths."""
        return list(self.agents.keys()) 