# ================================
# reasoning/coordination/agent_coordinator.py
# ================================

import asyncio
from typing import Dict, Any, List, Optional
from .task_router import TaskRouter

class AgentCoordinator:
    """
    Coordinates between Browser Use and Desktop agents
    Manages data flow and execution sequencing for hybrid workflows
    """
    
    def __init__(self):
        """Initialize agent coordinator"""
        self.router = TaskRouter()
        self.execution_history = []
        self.shared_data = {}
        
        print("🤝 Agent Coordinator initialized")
    
    async def execute_coordinated_task(
        self, 
        user_command: str,
        browser_agent=None,
        desktop_agent=None
    ) -> Dict[str, Any]:
        """
        Execute task with appropriate agent coordination
        
        Args:
            user_command: User's task description
            browser_agent: Browser Use agent instance (optional)
            desktop_agent: Desktop automation agent instance (optional)
            
        Returns:
            Execution result with data from all involved agents
        """
        
        print(f"🤝 Coordinating task: {user_command}")
        
        # Classify task
        classification = await self.router.classify_task(user_command)
        agent_type = classification['agent_type']
        confidence = classification['confidence']
        
        print(f"📊 Classification: {agent_type} (confidence: {confidence:.2f})")
        
        # Execute based on classification
        if agent_type == 'browser':
            return await self._execute_browser_task(user_command, browser_agent)
        elif agent_type == 'desktop':
            return await self._execute_desktop_task(user_command, desktop_agent)
        else:  # hybrid
            return await self._execute_hybrid_workflow(user_command, browser_agent, desktop_agent)
    
    async def _execute_browser_task(self, command: str, browser_agent) -> Dict[str, Any]:
        """Execute web-focused task using Browser Use"""
        
        print("🌐 Executing browser task")
        
        if browser_agent is None:
            # Create direct Browser Use implementation
            try:
                from browser_use import Agent, ChatOpenAI
                
                agent = Agent(
                    task=command,
                    llm=ChatOpenAI(model="gpt-4o-mini"),
                )
                
                result = await agent.run()
                
                return {
                    'success': True,
                    'agent_used': 'browser_use_direct',
                    'result': result,
                    'data': self._extract_browser_data(result),
                    'coordination_type': 'single_agent'
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'agent_used': 'browser_use_direct'
                }
        
        # Use provided browser agent
        result = await browser_agent.execute_task(command)
        result['coordination_type'] = 'single_agent'
        return result
    
    async def _execute_desktop_task(self, command: str, desktop_agent) -> Dict[str, Any]:
        """Execute desktop task using PyAutoGUI system"""
        
        print("💻 Executing desktop task")
        
        if desktop_agent is None:
            # Create direct PyAutoGUI implementation
            try:
                from desktop_agent.core.desktop_agent import DesktopAgent
                desktop_agent = DesktopAgent()
            except ImportError:
                # Fallback implementation
                return await self._create_fallback_desktop_result(command)
        
        result = await desktop_agent.execute_task(command)
        result['coordination_type'] = 'single_agent'
        return result
    
    async def _execute_hybrid_workflow(self, command: str, browser_agent, desktop_agent) -> Dict[str, Any]:
        """Execute coordinated browser + desktop workflow"""
        
        print("🔄 Executing hybrid workflow")
        
        # Parse command into workflow phases
        workflow_phases = self._parse_hybrid_command(command)
        
        results = []
        combined_data = {}
        
        for phase in workflow_phases:
            print(f"📋 Phase: {phase['description']}")
            
            if phase['agent'] == 'browser':
                result = await self._execute_browser_task(phase['task'], browser_agent)
            else:  # desktop
                result = await self._execute_desktop_task(phase['task'], desktop_agent)
            
            results.append(result)
            
            # Collect data for next phase
            if result.get('success') and result.get('data'):
                combined_data.update(result['data'])
                self.shared_data.update(result['data'])
        
        # Determine overall success
        overall_success = all(r.get('success', False) for r in results)
        
        return {
            'success': overall_success,
            'coordination_type': 'hybrid_workflow',
            'phases_executed': len(workflow_phases),
            'phase_results': results,
            'combined_data': combined_data,
            'original_command': command
        }
    
    def _parse_hybrid_command(self, command: str) -> List[Dict[str, str]]:
        """Parse hybrid command into executable phases"""
        
        command_lower = command.lower()
        
        # Pattern: "research X and save to file"
        if 'research' in command_lower and 'save' in command_lower:
            return [
                {
                    'agent': 'browser',
                    'task': f"Research and gather information about: {command}",
                    'description': 'Web research phase'
                },
                {
                    'agent': 'desktop', 
                    'task': 'Save research results to local file',
                    'description': 'Local file saving phase'
                }
            ]
        
        # Pattern: "download X and organize"
        elif 'download' in command_lower and ('organize' in command_lower or 'folder' in command_lower):
            return [
                {
                    'agent': 'browser',
                    'task': f"Find and download: {command}",
                    'description': 'Web download phase'
                },
                {
                    'agent': 'desktop',
                    'task': 'Organize downloaded files into folders',
                    'description': 'File organization phase'
                }
            ]
        
        # Default: try browser first, then desktop processing
        else:
            return [
                {
                    'agent': 'browser',
                    'task': command,
                    'description': 'Primary web execution'
                },
                {
                    'agent': 'desktop',
                    'task': f"Process results from: {command}",
                    'description': 'Desktop post-processing'
                }
            ]
    
    def _extract_browser_data(self, browser_result) -> Dict[str, Any]:
        """Extract useful data from Browser Use results"""
        
        try:
            data = {}
            
            if hasattr(browser_result, 'extracted_content'):
                data['content'] = browser_result.extracted_content()
            
            if hasattr(browser_result, 'urls'):
                data['urls'] = browser_result.urls()
            
            if hasattr(browser_result, 'action_results'):
                data['actions'] = [str(action) for action in browser_result.action_results()]
            
            return data
        except:
            return {'raw_result': str(browser_result)}
    
    async def _create_fallback_desktop_result(self, command: str) -> Dict[str, Any]:
        """Create fallback desktop result when agent not available"""
        
        return {
            'success': False,
            'error': 'Desktop agent not available',
            'agent_used': 'fallback',
            'command': command,
            'suggestion': 'Desktop agent implementation needed'
        }