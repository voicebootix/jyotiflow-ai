#!/usr/bin/env python3
"""Test just the StandardResponse class definition"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, Union

# Copy the exact StandardResponse definition from dashboard.py
class StandardResponse(BaseModel):
    status: str
    message: str
    data: Union[Dict[str, Any], List[Any]] = Field(default_factory=dict)
    success: bool = Field(default=True, description="Backward compatibility field")
    
    @model_validator(mode='after')
    def set_success_from_status(self) -> 'StandardResponse':
        """Set success field based on status for backward compatibility"""
        self.success = self.status == "success"
        return self

def test_standard_response():
    print("🧪 Testing StandardResponse directly...")
    
    try:
        # Test with dict data
        response_dict = StandardResponse(
            status="success",
            message="Test with dict",
            data={"key": "value"}
        )
        print(f"✅ Dict data works: {response_dict.data}")
        
        # Test with list data (this was failing before)
        response_list = StandardResponse(
            status="success", 
            message="Test with list",
            data=[{"item": 1}, {"item": 2}]
        )
        print(f"✅ List data works: {response_list.data}")
        
        # Test with empty list (the actual failing case)
        response_empty = StandardResponse(
            status="success",
            message="Test with empty list",
            data=[]
        )
        print(f"✅ Empty list works: {response_empty.data}")
        
        print("🎉 ALL StandardResponse tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ StandardResponse test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_standard_response()
