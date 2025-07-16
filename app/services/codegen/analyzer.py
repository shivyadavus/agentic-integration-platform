"""
Integration analyzer for the agentic integration platform.

This module provides AI-powered analysis of integration requirements,
system compatibility assessment, and integration pattern recommendations.
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.services.ai.base import AIService, AIMessage, AIModelConfig
from app.services.ai.factory import AIServiceFactory
from app.services.ai.prompt_manager import prompt_manager
from app.services.knowledge.pattern_service import PatternService
from app.services.knowledge.entity_service import EntityService
from app.models.integration import IntegrationType
from app.models.knowledge import EntityType
from app.core.exceptions import ValidationError
from app.core.logging import LoggerMixin


@dataclass
class IntegrationAnalysis:
    """Results of integration requirement analysis."""
    
    integration_type: str
    data_flow: str
    complexity: str
    estimated_effort_hours: int
    key_challenges: List[str]
    recommended_approach: str
    data_transformations: List[Dict[str, Any]]
    error_handling_requirements: List[str]
    security_considerations: List[str]
    performance_requirements: Dict[str, Any]
    dependencies: List[str]
    testing_strategy: str
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "integration_type": self.integration_type,
            "data_flow": self.data_flow,
            "complexity": self.complexity,
            "estimated_effort_hours": self.estimated_effort_hours,
            "key_challenges": self.key_challenges,
            "recommended_approach": self.recommended_approach,
            "data_transformations": self.data_transformations,
            "error_handling_requirements": self.error_handling_requirements,
            "security_considerations": self.security_considerations,
            "performance_requirements": self.performance_requirements,
            "dependencies": self.dependencies,
            "testing_strategy": self.testing_strategy,
            "confidence_score": self.confidence_score,
        }


class IntegrationAnalyzer(LoggerMixin):
    """
    AI-powered integration requirements analyzer.
    
    Analyzes natural language integration specifications and provides
    structured analysis including complexity assessment, pattern recommendations,
    and implementation guidance.
    """
    
    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        pattern_service: Optional[PatternService] = None,
        entity_service: Optional[EntityService] = None
    ):
        """
        Initialize integration analyzer.
        
        Args:
            ai_service: AI service for analysis
            pattern_service: Pattern service for recommendations
            entity_service: Entity service for context
        """
        self.ai_service = ai_service or AIServiceFactory.get_default_service()
        self.pattern_service = pattern_service or PatternService()
        self.entity_service = entity_service or EntityService()
    
    async def analyze_integration_requirements(
        self,
        specification: str,
        source_system: Optional[Dict[str, Any]] = None,
        target_system: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> IntegrationAnalysis:
        """
        Analyze integration requirements from natural language specification.
        
        Args:
            specification: Natural language integration specification
            source_system: Source system information
            target_system: Target system information
            context: Additional context
            
        Returns:
            IntegrationAnalysis: Structured analysis results
        """
        try:
            self.logger.info("Starting integration requirements analysis")
            
            # Perform AI-powered analysis
            ai_analysis = await self._ai_analyze_requirements(
                specification, source_system, target_system, context
            )
            
            # Enhance with pattern recommendations
            pattern_recommendations = await self._get_pattern_recommendations(
                ai_analysis, source_system, target_system
            )
            
            # Create structured analysis
            analysis = self._create_analysis_from_ai_response(
                ai_analysis, pattern_recommendations
            )
            
            self.logger.info(
                "Integration analysis completed",
                integration_type=analysis.integration_type,
                complexity=analysis.complexity,
                confidence=analysis.confidence_score
            )
            
            return analysis
            
        except Exception as e:
            raise ValidationError(
                f"Integration analysis failed: {str(e)}",
                context={
                    "specification": specification[:200] + "..." if len(specification) > 200 else specification
                }
            )
    
    async def _ai_analyze_requirements(
        self,
        specification: str,
        source_system: Optional[Dict[str, Any]],
        target_system: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use AI to analyze integration requirements.
        
        Args:
            specification: Natural language specification
            source_system: Source system info
            target_system: Target system info
            context: Additional context
            
        Returns:
            Dict[str, Any]: AI analysis results
        """
        try:
            # Use integration analysis prompt
            prompt_text = prompt_manager.render_prompt(
                "integration_analysis",
                {
                    "requirement": specification,
                    "source_system": source_system,
                    "target_system": target_system,
                    "context": context
                }
            )
        except Exception:
            # Fallback prompt if template not found
            prompt_text = self._create_fallback_analysis_prompt(
                specification, source_system, target_system
            )
        
        messages = [AIMessage(role="user", content=prompt_text)]
        
        config = AIModelConfig(
            model=self.ai_service.default_model,
            temperature=0.2,  # Slightly higher for analysis creativity
            max_tokens=2048
        )
        
        response = await self.ai_service.generate_response(messages, config)
        
        # Parse JSON response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback parsing
            return self._parse_analysis_fallback(response.content)
    
    def _create_fallback_analysis_prompt(
        self,
        specification: str,
        source_system: Optional[Dict[str, Any]],
        target_system: Optional[Dict[str, Any]]
    ) -> str:
        """Create fallback analysis prompt."""
        prompt = f"""Analyze the following integration requirement and provide a structured analysis:

**Requirement:**
{specification}

Please provide your analysis in JSON format with the following structure:
{{
  "integration_type": "sync|async|webhook|batch|realtime|api_proxy|etl|event_driven",
  "data_flow": "unidirectional|bidirectional",
  "complexity": "low|medium|high",
  "estimated_effort_hours": number,
  "key_challenges": ["challenge1", "challenge2"],
  "recommended_approach": "detailed approach description",
  "data_transformations": [
    {{
      "source_field": "field_name",
      "target_field": "field_name",
      "transformation": "transformation_logic"
    }}
  ],
  "error_handling_requirements": ["requirement1", "requirement2"],
  "security_considerations": ["consideration1", "consideration2"],
  "performance_requirements": {{
    "throughput": "requests_per_second",
    "latency": "max_response_time_ms"
  }},
  "dependencies": ["dependency1", "dependency2"],
  "testing_strategy": "testing approach description"
}}"""
        
        if source_system:
            prompt += f"\n\n**Source System:** {source_system}"
        
        if target_system:
            prompt += f"\n\n**Target System:** {target_system}"
        
        return prompt
    
    def _parse_analysis_fallback(self, response: str) -> Dict[str, Any]:
        """Parse analysis response when JSON parsing fails."""
        # Extract key information using regex
        import re
        
        # Try to extract integration type
        integration_type_match = re.search(
            r"integration[_\s]*type[\"']?\s*:\s*[\"']?(\w+)",
            response,
            re.IGNORECASE
        )
        integration_type = integration_type_match.group(1) if integration_type_match else "sync"
        
        # Try to extract complexity
        complexity_match = re.search(
            r"complexity[\"']?\s*:\s*[\"']?(\w+)",
            response,
            re.IGNORECASE
        )
        complexity = complexity_match.group(1) if complexity_match else "medium"
        
        return {
            "integration_type": integration_type,
            "data_flow": "unidirectional",
            "complexity": complexity,
            "estimated_effort_hours": 8,
            "key_challenges": ["Data transformation", "Error handling"],
            "recommended_approach": "Standard API integration with proper error handling",
            "data_transformations": [],
            "error_handling_requirements": ["Retry logic", "Dead letter queue"],
            "security_considerations": ["Authentication", "Data encryption"],
            "performance_requirements": {
                "throughput": "100 requests/second",
                "latency": "500ms"
            },
            "dependencies": ["requests", "pydantic"],
            "testing_strategy": "Unit tests and integration tests",
            "ai_response": response
        }
    
    async def _get_pattern_recommendations(
        self,
        analysis: Dict[str, Any],
        source_system: Optional[Dict[str, Any]],
        target_system: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get pattern recommendations based on analysis.
        
        Args:
            analysis: AI analysis results
            source_system: Source system info
            target_system: Target system info
            
        Returns:
            List[Dict[str, Any]]: Pattern recommendations
        """
        # TODO: Implement pattern search with database session
        # For now, return mock recommendations
        return [
            {
                "id": "mock-pattern-1",
                "name": f"Standard {analysis.get('integration_type', 'sync')} Pattern",
                "type": analysis.get('integration_type', 'sync'),
                "description": "Standard integration pattern for this use case",
                "success_rate": 85.0,
                "usage_count": 25,
                "applicability_score": 0.8
            }
        ]
    
    def _create_analysis_from_ai_response(
        self,
        ai_analysis: Dict[str, Any],
        pattern_recommendations: List[Dict[str, Any]]
    ) -> IntegrationAnalysis:
        """
        Create structured analysis from AI response.
        
        Args:
            ai_analysis: AI analysis results
            pattern_recommendations: Pattern recommendations
            
        Returns:
            IntegrationAnalysis: Structured analysis
        """
        # Calculate confidence score based on response completeness
        confidence_score = self._calculate_confidence_score(ai_analysis)
        
        # Enhance recommended approach with patterns
        recommended_approach = ai_analysis.get("recommended_approach", "")
        if pattern_recommendations:
            pattern_names = [p["name"] for p in pattern_recommendations[:3]]
            recommended_approach += f"\n\nRecommended patterns: {', '.join(pattern_names)}"
        
        return IntegrationAnalysis(
            integration_type=ai_analysis.get("integration_type", "sync"),
            data_flow=ai_analysis.get("data_flow", "unidirectional"),
            complexity=ai_analysis.get("complexity", "medium"),
            estimated_effort_hours=ai_analysis.get("estimated_effort_hours", 8),
            key_challenges=ai_analysis.get("key_challenges", []),
            recommended_approach=recommended_approach,
            data_transformations=ai_analysis.get("data_transformations", []),
            error_handling_requirements=ai_analysis.get("error_handling_requirements", []),
            security_considerations=ai_analysis.get("security_considerations", []),
            performance_requirements=ai_analysis.get("performance_requirements", {}),
            dependencies=ai_analysis.get("dependencies", []),
            testing_strategy=ai_analysis.get("testing_strategy", ""),
            confidence_score=confidence_score
        )
    
    def _calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on analysis completeness.
        
        Args:
            analysis: AI analysis results
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        required_fields = [
            "integration_type", "data_flow", "complexity",
            "key_challenges", "recommended_approach"
        ]
        
        present_fields = sum(1 for field in required_fields if analysis.get(field))
        base_score = present_fields / len(required_fields)
        
        # Bonus for detailed fields
        if analysis.get("data_transformations"):
            base_score += 0.1
        
        if analysis.get("error_handling_requirements"):
            base_score += 0.1
        
        if analysis.get("security_considerations"):
            base_score += 0.1
        
        return min(1.0, base_score)
    
    async def assess_system_compatibility(
        self,
        source_system: Dict[str, Any],
        target_system: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess compatibility between two systems.
        
        Args:
            source_system: Source system information
            target_system: Target system information
            
        Returns:
            Dict[str, Any]: Compatibility assessment
        """
        compatibility = {
            "compatible": True,
            "compatibility_score": 0.8,
            "issues": [],
            "recommendations": [],
            "data_format_compatibility": {},
            "authentication_compatibility": {},
            "protocol_compatibility": {}
        }
        
        # Check data format compatibility
        source_format = source_system.get("data_format", "json").lower()
        target_format = target_system.get("data_format", "json").lower()
        
        if source_format == target_format:
            compatibility["data_format_compatibility"] = {
                "compatible": True,
                "transformation_required": False
            }
        else:
            compatibility["data_format_compatibility"] = {
                "compatible": True,
                "transformation_required": True,
                "transformation_type": f"{source_format}_to_{target_format}"
            }
            compatibility["recommendations"].append(
                f"Data transformation required: {source_format} → {target_format}"
            )
        
        # Check authentication compatibility
        source_auth = source_system.get("auth_type", "api_key").lower()
        target_auth = target_system.get("auth_type", "api_key").lower()
        
        compatibility["authentication_compatibility"] = {
            "source_auth": source_auth,
            "target_auth": target_auth,
            "compatible": True  # Assume compatible for now
        }
        
        # Check protocol compatibility
        source_protocol = source_system.get("protocol", "https").lower()
        target_protocol = target_system.get("protocol", "https").lower()
        
        compatibility["protocol_compatibility"] = {
            "source_protocol": source_protocol,
            "target_protocol": target_protocol,
            "compatible": source_protocol == target_protocol
        }
        
        if source_protocol != target_protocol:
            compatibility["issues"].append(
                f"Protocol mismatch: {source_protocol} vs {target_protocol}"
            )
            compatibility["compatibility_score"] -= 0.2
        
        return compatibility
    
    async def estimate_integration_complexity(
        self,
        specification: str,
        source_system: Optional[Dict[str, Any]] = None,
        target_system: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate integration complexity.
        
        Args:
            specification: Integration specification
            source_system: Source system info
            target_system: Target system info
            
        Returns:
            Dict[str, Any]: Complexity estimation
        """
        complexity_factors = {
            "data_volume": 1,
            "transformation_complexity": 1,
            "system_complexity": 1,
            "real_time_requirements": 1,
            "security_requirements": 1,
            "error_handling_complexity": 1
        }
        
        # Analyze specification for complexity indicators
        spec_lower = specification.lower()
        
        # Data volume indicators
        if any(word in spec_lower for word in ["bulk", "batch", "millions", "large"]):
            complexity_factors["data_volume"] = 3
        elif any(word in spec_lower for word in ["thousands", "many"]):
            complexity_factors["data_volume"] = 2
        
        # Real-time requirements
        if any(word in spec_lower for word in ["real-time", "immediate", "instant", "live"]):
            complexity_factors["real_time_requirements"] = 3
        elif any(word in spec_lower for word in ["near real-time", "quickly"]):
            complexity_factors["real_time_requirements"] = 2
        
        # Security requirements
        if any(word in spec_lower for word in ["secure", "encrypted", "authenticated", "authorized"]):
            complexity_factors["security_requirements"] = 2
        if any(word in spec_lower for word in ["compliance", "gdpr", "hipaa", "pci"]):
            complexity_factors["security_requirements"] = 3
        
        # Calculate overall complexity
        total_score = sum(complexity_factors.values())
        max_score = len(complexity_factors) * 3
        
        complexity_ratio = total_score / max_score
        
        if complexity_ratio <= 0.4:
            complexity_level = "low"
            estimated_hours = 4
        elif complexity_ratio <= 0.7:
            complexity_level = "medium"
            estimated_hours = 16
        else:
            complexity_level = "high"
            estimated_hours = 40
        
        return {
            "complexity_level": complexity_level,
            "complexity_score": complexity_ratio,
            "complexity_factors": complexity_factors,
            "estimated_hours": estimated_hours,
            "risk_factors": self._identify_risk_factors(specification, complexity_factors)
        }
    
    def _identify_risk_factors(
        self,
        specification: str,
        complexity_factors: Dict[str, int]
    ) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        if complexity_factors["data_volume"] >= 3:
            risks.append("High data volume may impact performance")
        
        if complexity_factors["real_time_requirements"] >= 3:
            risks.append("Real-time requirements increase system complexity")
        
        if complexity_factors["security_requirements"] >= 3:
            risks.append("High security requirements may slow development")
        
        spec_lower = specification.lower()
        
        if "legacy" in spec_lower:
            risks.append("Legacy system integration may have compatibility issues")
        
        if any(word in spec_lower for word in ["custom", "proprietary"]):
            risks.append("Custom/proprietary systems may lack documentation")
        
        return risks
