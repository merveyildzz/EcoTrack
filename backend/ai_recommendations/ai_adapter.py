"""
AI Adapter Module for EcoTrack
Provides abstracted interface for AI services (Gemini, OpenAI, etc.)
"""

import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from django.conf import settings
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Standardized AI response format"""
    content: str
    metadata: Dict[str, Any]
    provider: str
    model: str
    success: bool
    error_message: str = ""
    response_time_ms: int = 0
    token_count: Optional[int] = None
    cost_estimate: Optional[float] = None
    safety_flagged: bool = False


class AIAdapterBase(ABC):
    """Abstract base class for AI adapters"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__.lower().replace('adapter', '')
    
    @abstractmethod
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate text based on prompt and context"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI service is available"""
        pass


class GeminiAdapter(AIAdapterBase):
    """Google Gemini AI adapter"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            raise ImportError("google-generativeai package is required for Gemini adapter")
        
        api_key = api_key or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        super().__init__(api_key, model)
        self.genai.configure(api_key=self.api_key)
        
        # Configure safety settings
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate text using Gemini"""
        start_time = time.time()
        
        try:
            model = self.genai.GenerativeModel(
                model_name=self.model,
                safety_settings=self.safety_settings
            )
            
            # Add context to prompt if provided
            if context:
                context_str = f"Context: {json.dumps(context, indent=2)}\n\n"
                full_prompt = context_str + prompt
            else:
                full_prompt = prompt
            
            response = model.generate_content(full_prompt)
            response_time = int((time.time() - start_time) * 1000)
            
            # Check if response was blocked by safety filters
            if response.candidates and response.candidates[0].finish_reason.name == "SAFETY":
                return AIResponse(
                    content="",
                    metadata={"finish_reason": "SAFETY", "blocked": True},
                    provider="gemini",
                    model=self.model,
                    success=False,
                    error_message="Response blocked by safety filters",
                    response_time_ms=response_time,
                    safety_flagged=True
                )
            
            # Extract content
            content = response.text if response.text else ""
            
            # Extract metadata
            metadata = {
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN",
                "safety_ratings": [
                    {
                        "category": rating.category.name,
                        "probability": rating.probability.name
                    }
                    for rating in response.candidates[0].safety_ratings
                ] if response.candidates and response.candidates[0].safety_ratings else []
            }
            
            return AIResponse(
                content=content,
                metadata=metadata,
                provider="gemini",
                model=self.model,
                success=True,
                response_time_ms=response_time,
                token_count=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None
            )
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            logger.error(f"Gemini API error: {str(e)}")
            
            return AIResponse(
                content="",
                metadata={},
                provider="gemini",
                model=self.model,
                success=False,
                error_message=str(e),
                response_time_ms=response_time
            )
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        try:
            model = self.genai.GenerativeModel(self.model)
            response = model.generate_content("Test")
            return True
        except Exception:
            return False


class MockAIAdapter(AIAdapterBase):
    """Mock AI adapter for testing and fallback"""
    
    def __init__(self, model: str = "mock-ai"):
        super().__init__("mock-key", model)
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate mock response"""
        time.sleep(0.1)  # Simulate API latency
        
        # Simple rule-based responses
        mock_responses = {
            "daily": "Try walking or biking instead of driving today. Small changes make a big impact! 🚶‍♀️",
            "coaching": "Based on your recent activities, consider focusing on reducing energy consumption at home.",
            "product": "Consider switching to LED bulbs - they use 75% less energy than traditional bulbs.",
            "habit": "Great job on logging your activities! Try to maintain this consistency.",
            "goal": "You're making good progress! Consider increasing your daily CO₂ reduction goal by 10%."
        }
        
        # Determine response type based on prompt content
        prompt_lower = prompt.lower()
        if "daily" in prompt_lower:
            content = mock_responses["daily"]
        elif "coaching" in prompt_lower:
            content = mock_responses["coaching"]
        elif "product" in prompt_lower:
            content = mock_responses["product"]
        elif "habit" in prompt_lower:
            content = mock_responses["habit"]
        elif "goal" in prompt_lower:
            content = mock_responses["goal"]
        else:
            content = "Keep up the great work on reducing your carbon footprint!"
        
        return AIResponse(
            content=content,
            metadata={"mock": True, "prompt_length": len(prompt)},
            provider="mock",
            model=self.model,
            success=True,
            response_time_ms=100,
            token_count=len(content.split())
        )
    
    def is_available(self) -> bool:
        """Mock adapter is always available"""
        return True


class AIAdapterFactory:
    """Factory for creating AI adapters"""
    
    @staticmethod
    def create_adapter(provider: str = None) -> AIAdapterBase:
        """Create appropriate AI adapter based on configuration"""
        provider = provider or settings.AI_PROVIDER
        
        try:
            if provider == "gemini":
                return GeminiAdapter()
            elif provider == "mock":
                return MockAIAdapter()
            else:
                logger.warning(f"Unknown AI provider: {provider}, falling back to mock")
                return MockAIAdapter()
        except Exception as e:
            logger.error(f"Failed to create {provider} adapter: {e}, falling back to mock")
            return MockAIAdapter()
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available AI providers"""
        providers = []
        
        # Test Gemini
        try:
            adapter = GeminiAdapter()
            if adapter.is_available():
                providers.append("gemini")
        except Exception:
            pass
        
        # Mock is always available
        providers.append("mock")
        
        return providers