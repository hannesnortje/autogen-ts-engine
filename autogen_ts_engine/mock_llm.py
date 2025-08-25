"""
Mock LLM system for development and testing.
This simulates fast LLM responses without requiring a heavy model.
"""

import json
import time
from typing import Dict, List, Any, Optional
import requests
from unittest.mock import patch


class MockResponse:
    """Mock response object for requests."""
    
    def __init__(self, status_code: int, json_data: Dict[str, Any]):
        self.status_code = status_code
        self._json_data = json_data
    
    def json(self) -> Dict[str, Any]:
        return self._json_data


class MockLLM:
    """Mock LLM that provides fast, realistic responses for development."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.response_templates = {
            "planner": [
                "I'll create a comprehensive plan for this Python project. Let me break it down into manageable tasks.",
                "Based on the requirements, here's my development strategy with clear milestones.",
                "I'll structure this project with proper architecture and testing frameworks."
            ],
            "coder": [
                "I'll implement this feature with clean, well-documented code following Python best practices.",
                "Let me write the code with proper error handling and type hints.",
                "I'll create modular, testable code that follows the project's architecture."
            ],
            "tester": [
                "I'll create comprehensive tests to ensure code quality and reliability.",
                "Let me write unit tests and integration tests for this functionality.",
                "I'll test edge cases and ensure proper error handling."
            ],
            "critic": [
                "The code looks good overall, but here are some improvements for better maintainability.",
                "I see some areas where we can optimize performance and readability.",
                "The implementation is solid, but let's add some documentation and error handling."
            ],
            "rag": [
                "Based on the project context, here's relevant information to guide development.",
                "I found some useful patterns and best practices for this type of project.",
                "Here's the relevant documentation and examples for this feature."
            ]
        }
    
    def get_completion(self, messages: List[Dict[str, str]], model: str = "mock-model", max_tokens: int = 150) -> Dict[str, Any]:
        """Generate a mock completion response."""
        # Simulate a small delay (much faster than real LLM)
        time.sleep(0.1)
        
        # Determine agent type from the conversation
        agent_type = self._detect_agent_type(messages)
        
        # Get a template response
        template = self.response_templates.get(agent_type, self.response_templates["coder"])
        import random
        response_text = random.choice(template)
        
        # Add some context-specific content
        if "plan" in messages[-1]["content"].lower():
            response_text += " The plan includes: 1) Setup project structure, 2) Implement core features, 3) Add tests, 4) Documentation."
        elif "test" in messages[-1]["content"].lower():
            response_text += " I'll create test cases covering: unit tests, integration tests, and edge cases."
        elif "review" in messages[-1]["content"].lower():
            response_text += " The code follows good practices. Consider adding more comments for complex logic."
        
        return {
            "id": f"mock-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text,
                    "tool_calls": []
                },
                "logprobs": None,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(str(messages)) + len(response_text.split())
            }
        }
    
    def _detect_agent_type(self, messages: List[Dict[str, str]]) -> str:
        """Detect which type of agent is responding based on conversation context."""
        last_message = messages[-1]["content"].lower()
        
        if any(word in last_message for word in ["plan", "strategy", "architecture", "design"]):
            return "planner"
        elif any(word in last_message for word in ["implement", "code", "write", "create"]):
            return "coder"
        elif any(word in last_message for word in ["test", "testing", "verify", "validate"]):
            return "tester"
        elif any(word in last_message for word in ["review", "critique", "improve", "optimize"]):
            return "critic"
        elif any(word in last_message for word in ["context", "information", "documentation", "reference"]):
            return "rag"
        else:
            return "coder"  # Default


def mock_requests_post(url: str, json: Dict[str, Any] = None, **kwargs) -> MockResponse:
    """Mock requests.post for LLM API calls."""
    if "/chat/completions" in url:
        mock_llm = MockLLM()
        messages = json.get("messages", [])
        model = json.get("model", "mock-model")
        max_tokens = json.get("max_tokens", 150)
        
        response_data = mock_llm.get_completion(messages, model, max_tokens)
        return MockResponse(200, response_data)
    
    # For other requests, return a generic response
    return MockResponse(200, {"status": "ok"})


def mock_httpx_post(url: str, json: Dict[str, Any] = None, **kwargs) -> MockResponse:
    """Mock httpx.post for LLM API calls."""
    if "/chat/completions" in str(url):
        mock_llm = MockLLM()
        messages = json.get("messages", [])
        model = json.get("model", "mock-model")
        max_tokens = json.get("max_tokens", 150)
        
        response_data = mock_llm.get_completion(messages, model, max_tokens)
        return MockResponse(200, response_data)
    
    # For other requests, return a generic response
    return MockResponse(200, {"status": "ok"})


def enable_mock_llm():
    """Enable mock LLM by patching both requests.post and httpx.post."""
    patches = [
        patch('requests.post', side_effect=mock_requests_post),
        patch('httpx.post', side_effect=mock_httpx_post),
        patch('httpx.Client.post', side_effect=mock_httpx_post)
    ]
    return patches


def disable_mock_llm():
    """Disable mock LLM and restore original requests.post."""
    import requests
    # This will restore the original requests.post
    pass
