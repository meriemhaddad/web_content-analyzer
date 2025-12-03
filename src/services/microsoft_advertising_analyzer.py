"""
Microsoft Advertising eligibility analyzer for content compliance and brand safety.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
import re
from urllib.parse import urlparse
import aiohttp
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Microsoft Advertising compliance levels."""
    APPROVED = "approved"
    CONDITIONAL = "conditional"  
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"

class MicrosoftAdvertisingEligibilityAnalyzer:
    """
    Analyzes content for Microsoft Advertising compliance and eligibility.
    Implements Microsoft's advertising policies and brand safety requirements.
    """
    
    def __init__(self):
        self.settings = get_settings()
        
        # Microsoft Advertising policy categories
        self.prohibited_content = {
            "adult_content": ["adult", "porn", "xxx", "erotic", "sexual"],
            "violence": ["violence", "weapon", "gun", "bomb", "terror"],
            "illegal_activities": ["drugs", "illegal", "piracy", "fraud"],
            "gambling": ["casino", "gambling", "poker", "betting"],
            "hate_speech": ["hate", "racist", "discrimination"],
            "misleading": ["scam", "fake", "misleading", "clickbait"]
        }
        
        # Preferred content categories for Microsoft Advertising
        self.preferred_content = {
            "business": ["business", "enterprise", "professional", "industry"],
            "technology": ["technology", "software", "innovation", "digital"],
            "education": ["education", "learning", "training", "academic"],
            "healthcare": ["health", "medical", "wellness", "fitness"],
            "finance": ["finance", "investment", "banking", "financial"]
        }
        
    async def analyze_eligibility(
        self, 
        content_analysis: Dict[str, Any],
        url_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze content eligibility for Microsoft Advertising.
        
        Args:
            content_analysis: Existing content analysis from Azure OpenAI
            url_metadata: URL metadata and technical information
            
        Returns:
            Comprehensive Microsoft Advertising eligibility analysis
        """
        
        # Extract content for analysis
        url = url_metadata.get("url", "")
        title = content_analysis.get("metadata", {}).get("title", "")
        content_summary = content_analysis.get("content_summary", "")
        primary_category = content_analysis.get("primary_category", "")
        sentiment = content_analysis.get("sentiment", {})
        
        # Perform compliance checks
        brand_safety_score = await self._calculate_brand_safety_score(
            title, content_summary, primary_category, sentiment
        )
        
        technical_compliance = await self._check_technical_compliance(url, url_metadata)
        content_policy_compliance = await self._check_content_policy(
            title, content_summary, primary_category
        )
        
        # Calculate overall eligibility
        overall_score = await self._calculate_overall_eligibility(
            brand_safety_score, technical_compliance, content_policy_compliance
        )
        
        return {
            "url": url,
            "microsoft_advertising_eligible": overall_score["eligible"],
            "compliance_level": overall_score["compliance_level"],
            "overall_score": overall_score["score"],
            "brand_safety": brand_safety_score,
            "technical_compliance": technical_compliance,
            "content_policy": content_policy_compliance,
            "recommendations": await self._generate_recommendations(overall_score),
            "analysis_timestamp": content_analysis.get("timestamp"),
            "analyzer_version": "microsoft_advertising_v1.0"
        }
    
    async def _calculate_brand_safety_score(
        self,
        title: str,
        content: str,
        category: str,
        sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate Microsoft brand safety score."""
        
        combined_text = f"{title} {content}".lower()
        
        # Check for prohibited content
        prohibited_score = 0
        flagged_categories = []
        
        for category_name, keywords in self.prohibited_content.items():
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            if matches > 0:
                prohibited_score += matches
                flagged_categories.append(category_name)
        
        # Check for preferred content
        preferred_score = 0
        preferred_categories = []
        
        for category_name, keywords in self.preferred_content.items():
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            if matches > 0:
                preferred_score += matches
                preferred_categories.append(category_name)
        
        # Sentiment analysis for brand safety
        sentiment_score = sentiment.get("confidence", 0) if sentiment.get("overall") == "positive" else 0
        
        # Calculate final brand safety score (0-100)
        base_score = max(0, 100 - (prohibited_score * 20))  # Penalize prohibited content heavily
        base_score += min(20, preferred_score * 5)  # Reward preferred content
        base_score += sentiment_score * 10  # Boost for positive sentiment
        
        final_score = min(100, max(0, base_score))
        
        return {
            "score": round(final_score, 2),
            "prohibited_content_detected": len(flagged_categories) > 0,
            "flagged_categories": flagged_categories,
            "preferred_content_detected": len(preferred_categories) > 0,
            "preferred_categories": preferred_categories,
            "sentiment_contribution": sentiment_score,
            "safety_level": self._get_safety_level(final_score)
        }
    
    async def _check_technical_compliance(
        self, 
        url: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check technical compliance for Microsoft Advertising."""
        
        parsed_url = urlparse(url)
        compliance_checks = {}
        score = 100
        
        # HTTPS requirement (mandatory for Microsoft Advertising)
        https_compliant = parsed_url.scheme == "https"
        compliance_checks["https_enabled"] = https_compliant
        if not https_compliant:
            score -= 50  # Major penalty
        
        # Domain reputation (basic checks)
        domain_checks = await self._check_domain_reputation(parsed_url.netloc)
        compliance_checks.update(domain_checks)
        if not domain_checks.get("domain_trustworthy", True):
            score -= 30
        
        # Content type check
        content_type = metadata.get("content_type", "").lower()
        valid_content_type = "text/html" in content_type
        compliance_checks["valid_content_type"] = valid_content_type
        if not valid_content_type:
            score -= 20
        
        # Page accessibility (basic check)
        has_title = bool(metadata.get("title"))
        has_description = bool(metadata.get("description"))
        compliance_checks["has_metadata"] = has_title and has_description
        if not (has_title and has_description):
            score -= 15
        
        final_score = max(0, score)
        
        return {
            "score": final_score,
            "checks": compliance_checks,
            "compliant": final_score >= 70,
            "requirements_met": sum(1 for check in compliance_checks.values() if check),
            "total_requirements": len(compliance_checks)
        }
    
    async def _check_content_policy(
        self,
        title: str,
        content: str,
        category: str
    ) -> Dict[str, Any]:
        """Check Microsoft Advertising content policy compliance."""
        
        combined_text = f"{title} {content}".lower()
        
        # Policy violations check
        violations = []
        severity_score = 0
        
        # Adult content policy
        adult_keywords = ["adult", "sexual", "erotic", "porn", "xxx"]
        if any(keyword in combined_text for keyword in adult_keywords):
            violations.append({"policy": "adult_content", "severity": "high"})
            severity_score += 50
        
        # Violence policy
        violence_keywords = ["violence", "violent", "weapon", "gun", "bomb"]
        if any(keyword in combined_text for keyword in violence_keywords):
            violations.append({"policy": "violence", "severity": "high"})
            severity_score += 40
        
        # Misleading content policy
        misleading_keywords = ["scam", "fake", "misleading", "too good to be true"]
        if any(keyword in combined_text for keyword in misleading_keywords):
            violations.append({"policy": "misleading_content", "severity": "medium"})
            severity_score += 25
        
        # Gambling policy
        gambling_keywords = ["gambling", "casino", "betting", "poker"]
        if any(keyword in combined_text for keyword in gambling_keywords):
            violations.append({"policy": "gambling", "severity": "medium"})
            severity_score += 30
        
        # Calculate compliance score
        compliance_score = max(0, 100 - severity_score)
        
        return {
            "score": compliance_score,
            "compliant": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations),
            "severity_score": severity_score,
            "compliance_level": self._get_compliance_level(compliance_score, violations)
        }
    
    async def _check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Basic domain reputation checks."""
        
        # Known safe domain patterns
        trusted_tlds = [".gov", ".edu", ".org"]
        trusted_domains = ["microsoft.com", "github.com", "stackoverflow.com", "linkedin.com"]
        
        is_trusted_tld = any(domain.endswith(tld) for tld in trusted_tlds)
        is_trusted_domain = any(trusted in domain for trusted in trusted_domains)
        
        # Basic domain validation
        is_valid_domain = bool(re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$', domain))
        
        return {
            "domain_trustworthy": is_trusted_tld or is_trusted_domain or is_valid_domain,
            "is_trusted_tld": is_trusted_tld,
            "is_trusted_domain": is_trusted_domain,
            "is_valid_format": is_valid_domain
        }
    
    def _get_safety_level(self, score: float) -> str:
        """Get brand safety level based on score."""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "moderate"
        elif score >= 40:
            return "poor"
        else:
            return "unsafe"
    
    def _get_compliance_level(self, score: float, violations: List[Dict]) -> ComplianceLevel:
        """Get compliance level based on score and violations."""
        if len(violations) == 0 and score >= 90:
            return ComplianceLevel.APPROVED
        elif len(violations) == 0 and score >= 70:
            return ComplianceLevel.CONDITIONAL
        elif any(v["severity"] == "high" for v in violations):
            return ComplianceLevel.PROHIBITED
        else:
            return ComplianceLevel.RESTRICTED
    
    async def _calculate_overall_eligibility(
        self,
        brand_safety: Dict[str, Any],
        technical: Dict[str, Any],
        content_policy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall Microsoft Advertising eligibility."""
        
        # Weighted scoring
        brand_safety_weight = 0.4
        technical_weight = 0.3
        content_policy_weight = 0.3
        
        overall_score = (
            brand_safety["score"] * brand_safety_weight +
            technical["score"] * technical_weight +
            content_policy["score"] * content_policy_weight
        )
        
        # Determine eligibility
        eligible = (
            overall_score >= 70 and
            technical["compliant"] and
            content_policy["compliant"] and
            brand_safety["score"] >= 60
        )
        
        # Determine compliance level
        if overall_score >= 90 and eligible:
            compliance_level = ComplianceLevel.APPROVED
        elif overall_score >= 70 and eligible:
            compliance_level = ComplianceLevel.CONDITIONAL
        elif overall_score >= 50:
            compliance_level = ComplianceLevel.RESTRICTED
        else:
            compliance_level = ComplianceLevel.PROHIBITED
        
        return {
            "score": round(overall_score, 2),
            "eligible": eligible,
            "compliance_level": compliance_level.value,
            "component_scores": {
                "brand_safety": brand_safety["score"],
                "technical": technical["score"],
                "content_policy": content_policy["score"]
            }
        }
    
    async def _generate_recommendations(self, eligibility_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving Microsoft Advertising eligibility."""
        
        recommendations = []
        score = eligibility_result["score"]
        compliance_level = eligibility_result["compliance_level"]
        
        if compliance_level == ComplianceLevel.PROHIBITED.value:
            recommendations.append("Content violates Microsoft Advertising policies and cannot be approved")
            recommendations.append("Review content for prohibited material and brand safety concerns")
        
        elif compliance_level == ComplianceLevel.RESTRICTED.value:
            recommendations.append("Content requires review and modification for advertising approval")
            if score < 60:
                recommendations.append("Improve content quality and brand safety measures")
        
        elif compliance_level == ComplianceLevel.CONDITIONAL.value:
            recommendations.append("Content is eligible with minor improvements")
            if eligibility_result["component_scores"]["technical"] < 80:
                recommendations.append("Improve technical compliance (HTTPS, metadata, performance)")
        
        else:  # APPROVED
            recommendations.append("Content fully complies with Microsoft Advertising policies")
            recommendations.append("Ready for advertising campaign integration")
        
        return recommendations