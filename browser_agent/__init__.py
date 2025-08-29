"""
Browser Agent - Web automation using Browser Use library
Handles all web-based tasks: research, shopping, forms, social media
"""

from .core import BrowserAgent, BrowserExecutor
from .tools import BrowserController, WebDataExtractor

__all__ = ["BrowserAgent", "BrowserExecutor", "BrowserController", "WebDataExtractor"]
