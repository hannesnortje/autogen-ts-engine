"""
Gemini LLM Adapter for AutoGen TS Engine

This module provides integration with Google's Gemini API for LLM functionality.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available. Install with: pip install google-generativeai")

from .schemas import LLMBinding, LLMProvider


class GeminiAdapter:
    """Adapter for Google Gemini API integration."""
    
    def __init__(self, llm_binding: LLMBinding):
        """Initialize Gemini adapter."""
        self.llm_binding = llm_binding
        self.logger = logging.getLogger(__name__)
        
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI not available. Install with: pip install google-generativeai")
        
        # Configure Gemini
        self._configure_gemini()
        
        # Initialize model
        self.model = self._get_model()
        
    def _configure_gemini(self):
        """Configure Gemini API."""
        api_key = self.llm_binding.api_key
        
        # Check for environment variable if no API key provided
        if not api_key or api_key == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable or provide in config.")
        
        genai.configure(api_key=api_key)
        self.logger.info("Gemini API configured successfully")
    
    def _get_model(self):
        """Get the appropriate Gemini model."""
        model_name = self.llm_binding.model_name
        
        # Map common model names to Gemini models
        model_mapping = {
            "gemini-pro": "gemini-1.5-pro",
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-pro-vision": "gemini-1.5-pro",
            "default": "gemini-1.5-flash"  # Fastest for testing
        }
        
        gemini_model = model_mapping.get(model_name, model_mapping["default"])
        
        try:
            model = genai.GenerativeModel(gemini_model)
            self.logger.info(f"Using Gemini model: {gemini_model}")
            return model
        except Exception as e:
            self.logger.error(f"Failed to load Gemini model {gemini_model}: {e}")
            # Fallback to default model
            model = genai.GenerativeModel("gemini-1.5-flash")
            self.logger.info("Using fallback Gemini model: gemini-1.5-flash")
            return model
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response using Gemini."""
        try:
            # Configure generation parameters
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": max_tokens or 2048,
            }
            
            # Configure safety settings
            safety_settings = [
                {
                    "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                    "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
            ]
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            if response.text:
                return response.text
            else:
                self.logger.warning("Empty response from Gemini")
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            self.logger.error(f"Error generating response with Gemini: {e}")
            return f"Error: {str(e)}"
    
    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Generate code using Gemini."""
        code_prompt = f"""
        You are an expert {language} developer. Generate clean, well-documented code based on the following requirements:
        
        {prompt}
        
        Requirements:
        1. Use modern {language} best practices
        2. Include proper error handling
        3. Add clear comments and docstrings
        4. Follow PEP 8 style guidelines (if Python)
        5. Make the code production-ready
        
        Generate only the code, no explanations.
        """
        
        return self.generate_response(code_prompt, max_tokens=4096)
    
    def analyze_code(self, code: str, language: str = "python") -> str:
        """Analyze code and provide feedback using Gemini."""
        analysis_prompt = f"""
        You are a senior {language} developer and code reviewer. Analyze the following code and provide feedback:
        
        ```{language}
        {code}
        ```
        
        Please provide:
        1. Code quality assessment
        2. Potential improvements
        3. Security considerations
        4. Performance optimizations
        5. Best practices recommendations
        
        Be constructive and specific.
        """
        
        return self.generate_response(analysis_prompt)
    
    def get_autogen_config(self) -> Dict[str, Any]:
        """Get configuration for AutoGen integration."""
        return {
            "config_list": [{
                "model": "gemini-1.5-flash",
                "api_type": "google",
                "api_key": self.llm_binding.api_key,
            }],
            "cache_seed": self.llm_binding.cache_seed,
            "temperature": 0.7,
            "timeout": 120,  # Gemini is faster than LM Studio
        }


def create_gemini_adapter(llm_binding: LLMBinding) -> Optional[GeminiAdapter]:
    """Create a Gemini adapter if available and configured."""
    if llm_binding.provider != LLMProvider.GEMINI:
        return None
    
    try:
        return GeminiAdapter(llm_binding)
    except Exception as e:
        logging.error(f"Failed to create Gemini adapter: {e}")
        return None


def is_gemini_available() -> bool:
    """Check if Gemini is available."""
    return GEMINI_AVAILABLE


def get_gemini_models() -> List[str]:
    """Get available Gemini models."""
    return [
        "gemini-1.5-flash",  # Fastest, good for testing
        "gemini-1.5-pro",    # Most capable
        "gemini-pro",        # Legacy name
    ]
