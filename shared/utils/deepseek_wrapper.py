import os
import json
import requests
from typing import Dict, Any, List, Optional, Iterator
from dotenv import load_dotenv

load_dotenv()

class DeepSeekOpenAIWrapper:
    """
    Wrapper that makes DeepSeek API compatible with OpenAI interface
    Browser Use will think it's talking to OpenAI, but we route to DeepSeek
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        
        if not self.api_key:
            raise ValueError("DeepSeek API key not found. Set DEEPSEEK_API_KEY environment variable.")
        
        print("DeepSeek wrapper initialized - Browser Use will use DeepSeek under the hood")
    
    class ChatCompletion:
        """Mock OpenAI ChatCompletion class that routes to DeepSeek"""
        
        def __init__(self, wrapper_instance):
            self.wrapper = wrapper_instance
        
        def create(self, model: str, messages: List[Dict], temperature: float = 0.3, 
                  max_tokens: Optional[int] = None, stream: bool = False, **kwargs):
            
            # Map OpenAI model names to DeepSeek equivalents
            model_mapping = {
                "gpt-4": "deepseek-chat",
                "gpt-4o": "deepseek-chat", 
                "gpt-4o-mini": "deepseek-chat",
                "gpt-3.5-turbo": "deepseek-chat"
            }
            
            deepseek_model = model_mapping.get(model, "deepseek-chat")
            
            payload = {
                "model": deepseek_model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            headers = {
                "Authorization": f"Bearer {self.wrapper.api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(
                    f"{self.wrapper.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    stream=stream
                )
                response.raise_for_status()
                
                if stream:
                    return self._handle_streaming_response(response)
                else:
                    return self._create_openai_compatible_response(response.json())
                    
            except requests.exceptions.RequestException as e:
                raise Exception(f"DeepSeek API error: {e}")
        
        def _create_openai_compatible_response(self, deepseek_response: Dict) -> 'MockOpenAIResponse':
            """Convert DeepSeek response to OpenAI-compatible format"""
            return MockOpenAIResponse(deepseek_response)
    
    @property
    def chat(self):
        return type('Chat', (), {'completions': self.ChatCompletion(self)})()

class MockOpenAIResponse:
    """Mock OpenAI response object that Browser Use expects"""
    
    def __init__(self, deepseek_response: Dict):
        self.raw_response = deepseek_response
        
        if 'choices' in deepseek_response and len(deepseek_response['choices']) > 0:
            choice = deepseek_response['choices'][0]
            
            if 'message' in choice:
                self.content = choice['message'].get('content', '')
                self.role = choice['message'].get('role', 'assistant')
            else:
                self.content = ''
                self.role = 'assistant'
        else:
            self.content = ''
            self.role = 'assistant'
        
        # Create nested structure that Browser Use expects
        self.choices = [type('Choice', (), {
            'message': type('Message', (), {
                'content': self.content,
                'role': self.role
            })()
        })()]

def monkey_patch_openai():
    """Monkey patch OpenAI library to use DeepSeek instead"""
    
    try:
        import openai
        
        deepseek_wrapper = DeepSeekOpenAIWrapper()
        
        class PatchedOpenAIClient:
            def __init__(self, api_key=None, **kwargs):
                self.api_key = api_key
                self._deepseek = deepseek_wrapper
                print("Intercepted OpenAI client - routing to DeepSeek")
            
            @property
            def chat(self):
                return self._deepseek.chat
        
        openai.OpenAI = PatchedOpenAIClient
        
        print("Successfully monkey-patched OpenAI to use DeepSeek")
        return True
        
    except ImportError:
        print("OpenAI library not found - cannot monkey patch")
        return False
    except Exception as e:
        print(f"Failed to monkey patch OpenAI: {e}")
        return False
