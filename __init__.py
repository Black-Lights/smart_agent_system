"""
Smart Agent System - Multi-Agent Desktop Automation
Combines Browser Use (web automation) with Desktop automation (PyAutoGUI + OCR)
"""

from .core import MasterAgent, SystemOrchestrator
from .browser_agent import BrowserAgent
from .desktop_agent import DesktopAgent
from .reasoning import analyze_task, generate_steps

__version__ = "1.0.0"
__all__ = ["MasterAgent", "BrowserAgent", "DesktopAgent", "analyze_task", "generate_steps"]
