#!/usr/bin/env python3

import sys
from pathlib import Path

print("Testing AutoGen TS Engine with mock LLM responses...")

# Mock the requests module to return fast responses
import requests
original_post = requests.post
original_get = requests.get

def mock_post(*args, **kwargs):
    """Mock POST requests to return fast responses."""
    if 'chat/completions' in args[0]:
        # Return a mock completion response
        return type('MockResponse', (), {
            'status_code': 200,
            'json': lambda: {
                'choices': [{
                    'message': {
                        'content': 'This is a mock response for testing. The engine is working correctly.'
                    }
                }]
            }
        })()
    return original_post(*args, **kwargs)

def mock_get(*args, **kwargs):
    """Mock GET requests."""
    if 'models' in args[0]:
        return type('MockResponse', (), {
            'status_code': 200,
            'json': lambda: {'data': [{'id': 'mock-model'}]}
        })()
    return original_get(*args, **kwargs)

# Replace the real requests with mocks
requests.post = mock_post
requests.get = mock_get

# Now test the engine
try:
    from autogen_ts_engine.config_parser import ConfigParser
    from autogen_ts_engine.sprint_runner import SprintRunner
    from autogen_ts_engine.logging_utils import EngineLogger
    
    print("1. Parsing configuration...")
    cp = ConfigParser()
    settings = cp.parse_settings(Path('config'))
    agent_defs = cp.parse_agents(Path('config'))
    
    print("2. Creating logger and runner...")
    logger = EngineLogger()
    runner = SprintRunner(settings, logger)
    
    print("3. Running sprints with mock LLM...")
    results = runner.run_sprints(agent_defs)
    
    print(f"✅ Engine test completed! Results: {len(results)} sprints")
    for i, result in enumerate(results):
        print(f"   Sprint {i+1}: {'✅ Success' if result.success else '❌ Failed'}")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

# Restore original requests
requests.post = original_post
requests.get = original_get
