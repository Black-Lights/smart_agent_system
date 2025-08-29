"""
Enhanced Reasoning Engine - Multi-Model Support
Supports GPT-4, DeepSeek, Claude and other models via API
"""

from .task_reasoning.task_analyzer import TaskAnalyzer
from .step_reasoning.step_generator import StepGenerator
from .coordination.agent_coordinator import AgentCoordinator
from .coordination.task_router import TaskRouter

# Main interface functions
def analyze_task(user_command: str):
    """Analyze task and determine optimal agent routing"""
    analyzer = TaskAnalyzer()
    return analyzer.analyze_task(user_command)

def generate_steps(user_command: str, detection_data: dict, task_analysis: dict):
    """Generate detailed execution steps"""  
    generator = StepGenerator()
    return generator.generate_detailed_steps(user_command, detection_data, task_analysis)

__all__ = ["TaskAnalyzer", "StepGenerator", "AgentCoordinator", "TaskRouter", 
           "analyze_task", "generate_steps"]
