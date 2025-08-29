# ================================
# reasoning/step_reasoning.py  
# ================================

import os
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class StepReasoner:
    """
    Detailed step-by-step planning and execution logic.
    Works with UI detection data and OS context for precise actions.
    """
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.use_deepseek = bool(os.getenv("DEEPSEEK_API_KEY"))
        
        if self.use_deepseek:
            self.base_url = "https://api.deepseek.com/v1/chat/completions"
            self.model = "deepseek-chat"
            print("[Step Reasoner] Using DeepSeek API")
        else:
            self.base_url = "https://api.openai.com/v1/chat/completions"
            self.model = "gpt-4o"
            print("[Step Reasoner] Using OpenAI GPT-4o API")
    
    def generate_detailed_steps(
        self, 
        user_command: str,
        detection_data: Dict[str, Any],
        task_analysis: Dict[str, Any],
        os_context: str
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed, actionable steps based on current screen state.
        
        Args:
            user_command: Original user command
            detection_data: UI detector results (windows mode)
            task_analysis: Result from TaskReasoner
            os_context: OS and environment information
            
        Returns:
            List of detailed step dictionaries
        """
        
        # Extract relevant screen information
        screen_context = self._extract_screen_context(detection_data, user_command)
        
        # Determine agent type and context
        agent_type = task_analysis.get("agent_type", "desktop")
        required_context = task_analysis.get("required_context", "desktop")
        
        if agent_type == "browser":
            return self._generate_browser_steps(user_command, screen_context, os_context)
        elif agent_type == "desktop":
            return self._generate_desktop_steps(user_command, screen_context, os_context)
        else:  # hybrid
            return self._generate_hybrid_steps(user_command, screen_context, os_context)
    
    def _extract_screen_context(self, detection_data: Dict[str, Any], user_command: str) -> str:
        """Extract relevant screen information for step planning"""
        
        ui_elements = detection_data.get("ui_elements", [])
        text_elements = detection_data.get("text_elements", []) 
        windows_info = detection_data.get("windows", [])
        
        # Get window information
        window_context = ""
        if windows_info:
            active_windows = [w for w in windows_info if w.get("is_active", False)]
            if active_windows:
                window_context = f"Active Window: {active_windows[0].get('title', 'Unknown')}"
        
        # Extract key UI elements
        clickable_elements = []
        for elem in ui_elements[:15]:  # Limit to avoid token costs
            if elem.get("type") in ["button", "link", "input", "checkbox"]:
                clickable_elements.append(f"{elem.get('type', '')}: {elem.get('text', '')}")
        
        # Extract key text 
        visible_text = []
        command_keywords = user_command.lower().split()
        for elem in text_elements[:20]:
            text = elem.get("text", "").strip()
            if text and 3 < len(text) < 40:
                # Include text relevant to command
                if any(keyword in text.lower() for keyword in command_keywords):
                    visible_text.append(text)
        
        return f"""SCREEN STATE:
{window_context}

INTERACTIVE ELEMENTS:
{chr(10).join(clickable_elements[:10])}

RELEVANT TEXT:
{chr(10).join(visible_text[:10])}

TASK: {user_command}"""
    
    def _generate_browser_steps(self, command: str, screen_context: str, os_context: str) -> List[Dict[str, Any]]:
        """Generate steps for browser-based tasks"""
        
        prompt = f"""Generate precise browser automation steps for this web-based task.

{screen_context}

OS: {os_context}

TASK: {command}

Available Browser Actions:
- open_browser: Open browser with specific URL
- search_web: Search for information  
- click_element: Click on web elements
- fill_form: Fill web forms
- extract_data: Extract information from pages
- navigate: Navigate between pages
- download: Download files
- compare: Compare products/services

Generate detailed steps as JSON array:
[
  {{
    "step": 1,
    "action": "<action_type>",
    "target": "<specific target>", 
    "description": "<what this step accomplishes>",
    "expected_result": "<what should happen>"
  }}
]

Focus on accomplishing the user's goal effectively. Return only the JSON array."""
        
        try:
            response = self._call_api([
                {"role": "system", "content": "You are a browser automation specialist. Generate precise web automation steps."},
                {"role": "user", "content": prompt}
            ])
            
            steps = json.loads(response)
            return steps if isinstance(steps, list) else []
            
        except Exception as e:
            print(f"[Browser Steps Error] {e}")
            return [{"step": 1, "action": "open_browser", "target": "https://google.com", "description": "Fallback browser open"}]
    
    def _generate_desktop_steps(self, command: str, screen_context: str, os_context: str) -> List[Dict[str, Any]]:
        """Generate steps for desktop automation tasks"""
        
        prompt = f"""Generate precise desktop automation steps based on current screen state.

{screen_context}

OS: {os_context}

TASK: {command}

Available Desktop Actions:
- click_text: Click visible text/buttons (use EXACT text from screen)
- type: Type in focused field
- input_below: Find label and input below it  
- hotkey: Keyboard shortcuts (ctrl+c, alt+tab, etc.)
- focus_window: Switch to specific window
- open_app: Launch application
- terminal_command: Execute terminal command
- file_operation: File management operations

Generate steps as JSON array using EXACT text visible on screen:
[
  {{
    "step": 1,
    "type": "<action_type>",
    "target": "<exact text from screen>",
    "text": "<text to type if needed>",
    "description": "<what this accomplishes>"
  }}
]

CRITICAL: Use exact text from the screen context above. Return only JSON array."""
        
        try:
            response = self._call_api([
                {"role": "system", "content": "You are a desktop automation specialist. Use exact screen text for precise actions."},
                {"role": "user", "content": prompt}
            ])
            
            steps = json.loads(response)
            return steps if isinstance(steps, list) else []
            
        except Exception as e:
            print(f"[Desktop Steps Error] {e}")
            return [{"step": 1, "type": "click_text", "target": "fallback", "description": "Fallback action"}]
    
    def _generate_hybrid_steps(self, command: str, screen_context: str, os_context: str) -> List[Dict[str, Any]]:
        """Generate coordinated steps for tasks requiring both browser and desktop"""
        
        prompt = f"""This task requires both WEB and DESKTOP automation. Plan the coordination.

{screen_context}

OS: {os_context} 

TASK: {command}

Available Actions:
BROWSER: open_browser, search_web, extract_data, download
DESKTOP: file_operation, open_app, terminal_command, organize

Generate coordinated steps marking each as "browser" or "desktop":
[
  {{
    "step": 1,
    "agent": "browser|desktop", 
    "action": "<action_type>",
    "target": "<target>",
    "description": "<what this accomplishes>",
    "data_output": "<what data this produces for next agent>"
  }}
]

Plan the full workflow from web research to desktop delivery."""

        try:
            response = self._call_api([
                {"role": "system", "content": "You are a workflow coordinator specializing in web+desktop automation."},
                {"role": "user", "content": prompt}
            ])
            
            steps = json.loads(response) 
            return steps if isinstance(steps, list) else []
            
        except Exception as e:
            print(f"[Hybrid Steps Error] {e}")
            return [{"step": 1, "agent": "browser", "action": "search_web", "target": "google.com", "description": "Fallback search"}]
    
    def refine_failed_step(
        self,
        failed_step: Dict[str, Any], 
        error_message: str,
        current_screen_context: str,
        step_index: int,
        total_steps: int
    ) -> List[Dict[str, Any]]:
        """
        Analyze failed step and generate alternative approach.
        Can break complex steps into smaller substeps.
        """
        
        prompt = f"""A step failed during automation. Generate alternative approach.

FAILED STEP: {json.dumps(failed_step, indent=2)}
ERROR: {error_message}
STEP POSITION: {step_index + 1} of {total_steps}

CURRENT SCREEN:
{current_screen_context}

Generate 1-3 alternative steps that accomplish the same goal:
- Use different approach than the failed step
- Break into smaller steps if the original was too complex
- Use exact text/elements visible on current screen

Return JSON array:
[
  {{
    "type": "<action_type>",
    "target": "<exact_text_from_screen>", 
    "text": "<optional_text_to_type>",
    "description": "<alternative approach>",
    "retry_strategy": "<why this should work better>"
  }}
]"""

        try:
            response = self._call_api([
                {"role": "system", "content": "You are an automation troubleshooter. Generate alternative approaches for failed steps."},
                {"role": "user", "content": prompt}
            ])
            
            alternatives = json.loads(response)
            return alternatives if isinstance(alternatives, list) else []
            
        except Exception as e:
            print(f"[Step Refinement Error] {e}")
            return [{"type": "wait", "target": "1", "description": "Fallback wait step"}]
    
    def _call_api(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Call the configured API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"].strip()