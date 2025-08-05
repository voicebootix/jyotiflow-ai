#!/usr/bin/env python3
"""
Test script to verify schema imports work correctly

⚠️  SETUP: Set PYTHONPATH=backend or run from project root
Example: PYTHONPATH=backend python test_schema_imports.py
"""

try:
    # Test direct imports from schemas
    from schemas import StandardResponse
    from schemas import Campaign, ContentCalendarItem, GenerateAllAvatarPreviewsRequest
    from schemas import MarketingAsset, MarketingAssetCreate, MarketingOverview
    from schemas import PlatformConfig, PlatformConfigUpdate, TestConnectionRequest
    from schemas import PostExecutionRequest, PostExecutionResult, CampaignStatus
    from schemas import ContentStatus, YouTubePlatformStatus, FacebookPlatformStatus
    from schemas import InstagramPlatformStatus, TikTokPlatformStatus, BasePlatformStatus
    
    print("✅ All schema imports SUCCESSFUL!")
    print(f"✅ StandardResponse: {StandardResponse}")
    print(f"✅ Campaign: {Campaign}")
    print(f"✅ MarketingOverview: {MarketingOverview}")
    
    # Test import * 
    exec("from schemas import *")
    print("✅ Import * also SUCCESSFUL!")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")