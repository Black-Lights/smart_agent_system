# ================================
# reasoning/coordination/data_flow_manager.py
# ================================

import json
import os
from typing import Dict, Any, List
from datetime import datetime

class DataFlowManager:
    """
    Manages data sharing between agents
    Handles data persistence and inter-agent communication
    """
    
    def __init__(self, data_dir: str = "shared_data"):
        """Initialize data flow manager"""
        self.data_dir = data_dir
        self.session_data = {}
        self.data_history = []
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        print(f"📊 Data Flow Manager initialized (dir: {data_dir})")
    
    def store_agent_result(self, agent_name: str, task: str, result: Dict[str, Any]) -> str:
        """
        Store result from an agent for sharing with other agents
        
        Args:
            agent_name: Name of the agent (browser_agent, desktop_agent)
            task: Original task description
            result: Agent execution result
            
        Returns:
            Data ID for referencing this stored data
        """
        
        timestamp = datetime.now().isoformat()
        data_id = f"{agent_name}_{int(datetime.now().timestamp())}"
        
        data_entry = {
            'id': data_id,
            'agent': agent_name,
            'task': task,
            'result': result,
            'timestamp': timestamp
        }
        
        # Store in memory
        self.session_data[data_id] = data_entry
        self.data_history.append(data_entry)
        
        # Persist to file
        file_path = os.path.join(self.data_dir, f"{data_id}.json")
        with open(file_path, 'w') as f:
            json.dump(data_entry, f, indent=2)
        
        print(f"📁 Stored data from {agent_name}: {data_id}")
        return data_id
    
    def retrieve_agent_data(self, data_id: str) -> Dict[str, Any]:
        """Retrieve stored agent data by ID"""
        
        # Check memory first
        if data_id in self.session_data:
            return self.session_data[data_id]
        
        # Check file system
        file_path = os.path.join(self.data_dir, f"{data_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.session_data[data_id] = data  # Cache in memory
                return data
        
        return {}
    
    def get_latest_data_by_agent(self, agent_name: str) -> Dict[str, Any]:
        """Get the most recent data from a specific agent"""
        
        agent_entries = [entry for entry in self.data_history if entry['agent'] == agent_name]
        
        if agent_entries:
            return agent_entries[-1]  # Return most recent
        
        return {}
    
    def create_data_pipeline(self, source_agent: str, target_agent: str, data_transform=None) -> str:
        """
        Create a data pipeline between agents
        
        Args:
            source_agent: Agent providing the data
            target_agent: Agent consuming the data
            data_transform: Optional function to transform data between agents
            
        Returns:
            Pipeline ID
        """
        
        pipeline_id = f"pipeline_{source_agent}_to_{target_agent}_{int(datetime.now().timestamp())}"
        
        pipeline_config = {
            'id': pipeline_id,
            'source': source_agent,
            'target': target_agent,
            'transform': data_transform.__name__ if data_transform else None,
            'created': datetime.now().isoformat()
        }
        
        # Store pipeline configuration
        pipeline_path = os.path.join(self.data_dir, f"{pipeline_id}_config.json")
        with open(pipeline_path, 'w') as f:
            json.dump(pipeline_config, f, indent=2)
        
        print(f"🔗 Created data pipeline: {source_agent} → {target_agent}")
        return pipeline_id
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session data flow"""
        
        agent_counts = {}
        for entry in self.data_history:
            agent = entry['agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        return {
            'total_data_entries': len(self.data_history),
            'agents_involved': list(agent_counts.keys()),
            'data_per_agent': agent_counts,
            'latest_entry': self.data_history[-1] if self.data_history else None,
            'session_start': self.data_history[0]['timestamp'] if self.data_history else None
        }