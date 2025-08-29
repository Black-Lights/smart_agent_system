"""
Desktop Agent - Desktop automation using PyAutoGUI + OCR + UI Detection
Handles all desktop tasks: file management, applications, system control
"""

from .core import DesktopAgent, DesktopExecutor
from .tools import GUIController, FileOperationManager

__all__ = ["DesktopAgent", "DesktopExecutor", "GUIController", "FileOperationManager"]
