"""
Code validator for the agentic integration platform.

This module provides comprehensive validation of generated integration code,
including syntax checking, security analysis, and quality assessment.
"""

import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.services.ai.base import AIService, AIMessage, AIModelConfig
from app.services.ai.factory import AIServiceFactory
from app.services.ai.prompt_manager import prompt_manager
from app.core.exceptions import ValidationEngineError
from app.core.logging import LoggerMixin


class ValidationResult:
    """Represents code validation results."""
    
    def __init__(self):
        self.overall_score: float = 0.0
        self.syntax_valid: bool = False
        self.security_score: float = 0.0
        self.performance_score: float = 0.0
        self.maintainability_score: float = 0.0
        self.issues: List[Dict[str, Any]] = []
        self.strengths: List[str] = []
        self.recommendations: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "syntax_valid": self.syntax_valid,
            "security_score": self.security_score,
            "performance_score": self.performance_score,
            "maintainability_score": self.maintainability_score,
            "issues": self.issues,
            "strengths": self.strengths,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


class CodeValidator(LoggerMixin):
    """
    Comprehensive code validator for integration code.
    
    Provides syntax validation, security analysis, performance assessment,
    and maintainability scoring using both static analysis and AI.
    """
    
    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Initialize code validator.
        
        Args:
            ai_service: AI service for semantic validation
        """
        self.ai_service = ai_service or AIServiceFactory.get_default_service()
        
        # Security patterns to check
        self.security_patterns = {
            "sql_injection": [
                r"execute\s*\(\s*[\"'].*%.*[\"']\s*\)",
                r"cursor\.execute\s*\(\s*[\"'].*\+.*[\"']\s*\)",
                r"query\s*=.*\+.*",
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(",
                r"eval\s*\(",
                r"exec\s*\(",
            ],
            "hardcoded_secrets": [
                r"password\s*=\s*[\"'][^\"']+[\"']",
                r"api_key\s*=\s*[\"'][^\"']+[\"']",
                r"secret\s*=\s*[\"'][^\"']+[\"']",
                r"token\s*=\s*[\"'][^\"']+[\"']",
            ],
            "unsafe_deserialization": [
                r"pickle\.loads?\s*\(",
                r"yaml\.load\s*\(",
                r"json\.loads?\s*\(.*input",
            ],
        }
    
    async def validate_code(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Perform comprehensive code validation.
        
        Args:
            code: Code to validate
            language: Programming language
            context: Additional validation context
            
        Returns:
            ValidationResult: Validation results
        """
        result = ValidationResult()
        
        try:
            self.logger.info(f"Starting code validation for {language}")
            
            # Syntax validation
            result.syntax_valid = await self._validate_syntax(code, language)
            
            # Security analysis
            result.security_score = await self._analyze_security(code, language)
            
            # Performance analysis
            result.performance_score = await self._analyze_performance(code, language)
            
            # Maintainability analysis
            result.maintainability_score = await self._analyze_maintainability(code, language)
            
            # AI-powered semantic validation
            ai_validation = await self._ai_semantic_validation(code, language, context)
            result.issues.extend(ai_validation.get("issues", []))
            result.strengths.extend(ai_validation.get("strengths", []))
            result.recommendations.extend(ai_validation.get("recommendations", []))
            
            # Calculate overall score
            result.overall_score = self._calculate_overall_score(result)
            
            # Add metadata
            from datetime import datetime
            result.metadata = {
                "language": language,
                "line_count": len(code.split("\n")),
                "character_count": len(code),
                "validation_timestamp": datetime.utcnow().isoformat(),
            }
            
            self.logger.info(
                f"Code validation completed",
                overall_score=result.overall_score,
                syntax_valid=result.syntax_valid,
                issues_count=len(result.issues)
            )
            
            return result
            
        except Exception as e:
            raise ValidationEngineError(
                f"Code validation failed: {str(e)}",
                validation_type="comprehensive",
                context={"language": language, "code_length": len(code)}
            )
    
    async def _validate_syntax(self, code: str, language: str) -> bool:
        """
        Validate code syntax.
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            bool: True if syntax is valid
        """
        try:
            if language == "python":
                ast.parse(code)
                return True
            elif language == "javascript":
                # For JavaScript, we'd need a JS parser
                # For now, basic check
                return "function" in code or "=>" in code or "const" in code
            else:
                # For other languages, assume valid for now
                return True
                
        except SyntaxError as e:
            self.logger.warning(f"Syntax error in {language} code: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in syntax validation: {e}")
            return False
    
    async def _analyze_security(self, code: str, language: str) -> float:
        """
        Analyze code for security vulnerabilities.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            float: Security score (0.0 to 10.0)
        """
        if language != "python":
            return 8.0  # Default score for non-Python code
        
        security_issues = []
        
        # Check for security patterns
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, code, re.IGNORECASE)
                if matches:
                    security_issues.append({
                        "category": category,
                        "pattern": pattern,
                        "matches": len(matches)
                    })
        
        # Calculate security score
        if not security_issues:
            return 10.0
        
        # Deduct points based on severity
        score = 10.0
        for issue in security_issues:
            if issue["category"] in ["sql_injection", "command_injection"]:
                score -= 3.0  # Critical issues
            elif issue["category"] in ["hardcoded_secrets", "unsafe_deserialization"]:
                score -= 2.0  # High severity
            else:
                score -= 1.0  # Medium severity
        
        return max(0.0, score)
    
    async def _analyze_performance(self, code: str, language: str) -> float:
        """
        Analyze code for performance issues.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            float: Performance score (0.0 to 10.0)
        """
        if language != "python":
            return 8.0  # Default score
        
        score = 10.0
        
        # Check for performance anti-patterns
        performance_issues = []
        
        # Inefficient loops
        if re.search(r"for.*in.*range\(len\(", code):
            performance_issues.append("Inefficient loop pattern")
            score -= 1.0
        
        # Synchronous I/O in async context
        if "async def" in code and re.search(r"requests\.|urllib\.", code):
            performance_issues.append("Synchronous I/O in async function")
            score -= 2.0
        
        # Missing connection pooling
        if "requests." in code and "Session" not in code:
            performance_issues.append("Missing connection pooling")
            score -= 1.0
        
        # Inefficient string concatenation
        if re.search(r"\+.*[\"'].*\+", code):
            performance_issues.append("Inefficient string concatenation")
            score -= 0.5
        
        # Check for async/await usage (positive)
        if "async def" in code and "await" in code:
            score += 1.0  # Bonus for async usage
        
        return max(0.0, min(10.0, score))
    
    async def _analyze_maintainability(self, code: str, language: str) -> float:
        """
        Analyze code maintainability.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            float: Maintainability score (0.0 to 10.0)
        """
        score = 5.0  # Base score
        
        # Check for good practices
        if '"""' in code or "'''" in code:
            score += 1.0  # Docstrings
        
        if "def " in code:
            score += 1.0  # Functions defined
        
        if "class " in code:
            score += 1.0  # Classes defined
        
        if "import " in code:
            score += 0.5  # Proper imports
        
        if "try:" in code and "except" in code:
            score += 1.0  # Error handling
        
        if "logging" in code or "logger" in code:
            score += 1.0  # Logging
        
        if "->" in code:  # Type hints
            score += 1.0
        
        # Check for bad practices
        lines = code.split("\n")
        
        # Long functions
        in_function = False
        function_length = 0
        for line in lines:
            if line.strip().startswith("def "):
                if in_function and function_length > 50:
                    score -= 1.0  # Long function
                in_function = True
                function_length = 0
            elif in_function:
                function_length += 1
        
        # Deep nesting
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)
        
        if max_indent > 4:
            score -= 1.0  # Too much nesting
        
        return max(0.0, min(10.0, score))
    
    async def _ai_semantic_validation(
        self,
        code: str,
        language: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform AI-powered semantic validation.
        
        Args:
            code: Code to validate
            language: Programming language
            context: Validation context
            
        Returns:
            Dict[str, Any]: AI validation results
        """
        try:
            # Use validation prompt
            prompt_text = prompt_manager.render_prompt(
                "code_validation",
                {"code": code, "language": language, "context": context}
            )
            
            messages = [AIMessage(role="user", content=prompt_text)]
            
            config = AIModelConfig(
                model=self.ai_service.default_model,
                temperature=0.1,
                max_tokens=2048
            )
            
            response = await self.ai_service.generate_response(messages, config)
            
            # Parse AI response (expecting JSON)
            import json
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_ai_response_fallback(response.content)
            
        except Exception as e:
            self.logger.warning(f"AI semantic validation failed: {e}")
            return {
                "issues": [],
                "strengths": [],
                "recommendations": ["Consider manual code review"]
            }
    
    def _parse_ai_response_fallback(self, response: str) -> Dict[str, Any]:
        """Parse AI response when JSON parsing fails."""
        return {
            "issues": [],
            "strengths": ["Code generated successfully"],
            "recommendations": ["Review the generated code manually"],
            "ai_response": response
        }
    
    def _calculate_overall_score(self, result: ValidationResult) -> float:
        """
        Calculate overall validation score.
        
        Args:
            result: Validation result
            
        Returns:
            float: Overall score (0.0 to 10.0)
        """
        if not result.syntax_valid:
            return 0.0
        
        # Weighted average of component scores
        weights = {
            "security": 0.3,
            "performance": 0.25,
            "maintainability": 0.25,
            "syntax": 0.2
        }
        
        syntax_score = 10.0 if result.syntax_valid else 0.0
        
        overall = (
            weights["security"] * result.security_score +
            weights["performance"] * result.performance_score +
            weights["maintainability"] * result.maintainability_score +
            weights["syntax"] * syntax_score
        )
        
        # Adjust based on critical issues
        critical_issues = [
            issue for issue in result.issues
            if issue.get("severity") == "critical"
        ]
        
        if critical_issues:
            overall *= 0.5  # Halve score for critical issues
        
        return round(overall, 1)
    
    async def validate_integration_requirements(
        self,
        code: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate code against specific integration requirements.
        
        Args:
            code: Code to validate
            requirements: Integration requirements
            
        Returns:
            Dict[str, Any]: Requirement validation results
        """
        results = {
            "requirements_met": {},
            "missing_requirements": [],
            "compliance_score": 0.0
        }
        
        total_requirements = len(requirements)
        met_requirements = 0
        
        for req_name, req_value in requirements.items():
            if req_name == "async_support" and req_value:
                met = "async def" in code and "await" in code
                results["requirements_met"][req_name] = met
                if met:
                    met_requirements += 1
                else:
                    results["missing_requirements"].append("Async/await support")
            
            elif req_name == "error_handling" and req_value:
                met = "try:" in code and "except" in code
                results["requirements_met"][req_name] = met
                if met:
                    met_requirements += 1
                else:
                    results["missing_requirements"].append("Error handling")
            
            elif req_name == "logging" and req_value:
                met = "logging" in code or "logger" in code
                results["requirements_met"][req_name] = met
                if met:
                    met_requirements += 1
                else:
                    results["missing_requirements"].append("Logging")
            
            elif req_name == "type_hints" and req_value:
                met = "->" in code and ":" in code
                results["requirements_met"][req_name] = met
                if met:
                    met_requirements += 1
                else:
                    results["missing_requirements"].append("Type hints")
        
        if total_requirements > 0:
            results["compliance_score"] = (met_requirements / total_requirements) * 100
        
        return results
