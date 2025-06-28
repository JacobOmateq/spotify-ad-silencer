"""
Simple license validation system for different monetization tiers
"""

import hashlib
import time
import json
from typing import Dict, Optional

class LicenseManager:
    def __init__(self):
        self.tiers = {
            "basic": {
                "features": ["ad_silencing"],
                "price": 0
            },
            "pro": {
                "features": ["ad_silencing", "custom_profiles", "auto_update", "priority_support"],
                "price": 9.99
            },
            "enterprise": {
                "features": ["ad_silencing", "custom_profiles", "auto_update", "priority_support", 
                           "multi_user", "usage_analytics", "api_access"],
                "price": 29.99
            }
        }
    
    def validate_license(self, license_key: str) -> Dict:
        """Validate license key and return tier info"""
        if not license_key:
            return {"valid": True, "tier": "basic", "features": self.tiers["basic"]["features"]}
        
        # Simple validation (in production, use proper crypto)
        parts = license_key.split("-")
        if len(parts) != 4:
            return {"valid": False, "tier": "basic", "features": []}
        
        tier = parts[0].lower()
        if tier in self.tiers:
            return {
                "valid": True, 
                "tier": tier, 
                "features": self.tiers[tier]["features"]
            }
        
        return {"valid": False, "tier": "basic", "features": []}
    
    def generate_license(self, tier: str, user_id: str) -> str:
        """Generate a license key (for testing)"""
        timestamp = str(int(time.time()))
        hash_input = f"{tier}-{user_id}-{timestamp}"
        hash_part = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        
        return f"{tier.upper()}-{user_id[:4].upper()}-{timestamp[-4:]}-{hash_part.upper()}"

# Usage example:
if __name__ == "__main__":
    lm = LicenseManager()
    
    # Generate test licenses
    basic_key = lm.generate_license("basic", "user123")
    pro_key = lm.generate_license("pro", "user123") 
    enterprise_key = lm.generate_license("enterprise", "user123")
    
    print("Test License Keys:")
    print(f"Basic: {basic_key}")
    print(f"Pro: {pro_key}")
    print(f"Enterprise: {enterprise_key}")
    
    # Test validation
    for key in [basic_key, pro_key, enterprise_key]:
        result = lm.validate_license(key)
        print(f"\nKey: {key}")
        print(f"Valid: {result['valid']}, Tier: {result['tier']}")
        print(f"Features: {result['features']}") 