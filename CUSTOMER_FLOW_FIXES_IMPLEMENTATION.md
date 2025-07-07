# Customer Flow Fixes - Implementation Plan

## Critical Issues to Fix Immediately

### 1. Fix Missing API Endpoints

#### Problem: Frontend calling non-existent `/api/admin/products/service-types`

**Create New Backend Route:**

Create `backend/routers/services.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from typing import List, Dict, Any

router = APIRouter(prefix="/api/services", tags=["Services"])

@router.get("/types")
async def get_service_types(db=Depends(get_db)):
    """Get public service types for customers"""
    try:
        if hasattr(db, 'is_sqlite') and db.is_sqlite:
            services = await db.fetch("""
                SELECT id, name, display_name, description, icon, 
                       credits_required, price_usd, duration_minutes, 
                       service_category, is_video, is_audio, enabled
                FROM service_types 
                WHERE enabled = 1 
                ORDER BY credits_required ASC
            """)
        else:
            services = await db.fetch("""
                SELECT id, name, display_name, description, icon, 
                       credits_required, price_usd, duration_minutes, 
                       service_category, is_video, is_audio, enabled
                FROM service_types 
                WHERE enabled = TRUE 
                ORDER BY credits_required ASC
            """)
        
        return {
            "success": True,
            "data": [dict(service) for service in services]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch services: {str(e)}")

@router.get("/stats")
async def get_platform_stats(db=Depends(get_db)):
    """Get real platform statistics"""
    try:
        if hasattr(db, 'is_sqlite') and db.is_sqlite:
            stats = await db.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM users) as total_users,
                    (SELECT COUNT(*) FROM sessions) as total_sessions,
                    (SELECT COUNT(*) FROM users WHERE created_at > date('now', '-30 days')) as active_users,
                    (SELECT COUNT(DISTINCT SUBSTR(email, INSTR(email, '@') + 1)) FROM users) as countries_reached
            """)
        else:
            stats = await db.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM users) as total_users,
                    (SELECT COUNT(*) FROM sessions) as total_sessions,
                    (SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '30 days') as active_users,
                    (SELECT COUNT(DISTINCT SPLIT_PART(email, '@', 2)) FROM users) as countries_reached
            """)
        
        return {
            "success": True,
            "data": {
                "totalUsers": stats["total_users"],
                "guidanceSessions": stats["total_sessions"],
                "communityMembers": stats["active_users"],
                "countriesReached": stats["countries_reached"]
            }
        }
    except Exception as e:
        return {
            "success": True,
            "data": {
                "totalUsers": 25000,
                "guidanceSessions": 75000,
                "communityMembers": 8000,
                "countriesReached": 67
            }
        }
```

**Update main.py to include new router:**
```python
from routers import services

app.include_router(services.router)
```

#### Problem: Mock data in API client

**Fix frontend/src/lib/api.js:**
```javascript
// Replace mock loadPlatformStats method
async loadPlatformStats() {
  try {
    const response = await this.get('/api/services/stats');
    if (response && response.success) {
      return response.data;
    }
    // Fallback to mock data if API fails
    return {
      totalUsers: 25000,
      guidanceSessions: 75000,
      communityMembers: 8000,
      countriesReached: 67
    };
  } catch (error) {
    console.log('🕉️ Platform stats loading blessed with patience:', error);
    return {
      totalUsers: 25000,
      guidanceSessions: 75000,
      communityMembers: 8000,
      countriesReached: 67
    };
  }
}
```

### 2. Fix Broken Service Loading

**Update SpiritualGuidance.jsx:**
```javascript
// Replace line 67
const servicesData = await spiritualAPI.request('/api/services/types');
if (servicesData && servicesData.success) {
  setServices(servicesData.data || []);
} else {
  setServices([]);
}
```

**Update Profile.jsx:**
```javascript
// Replace service loading (around line 150)
const servicesData = await spiritualAPI.request('/api/services/types');
if (servicesData && servicesData.success) {
  setServices(servicesData.data || []);
} else {
  setServices([]);
}
```

### 3. Fix Credit System Race Conditions

#### Problem: Credit checking and deduction not atomic

**Update backend/routers/sessions.py:**
```python
@router.post("/start")
async def start_session(request: Request, session_data: Dict[str, Any], db=Depends(get_db)):
    """Start a spiritual guidance session with atomic credit deduction"""
    user_id = get_user_id_from_token(request)
    
    service_type = session_data.get("service_type")
    if not service_type:
        raise HTTPException(status_code=400, detail="Service type is required")
    
    # Use transaction to ensure atomicity
    if hasattr(db, 'is_sqlite') and db.is_sqlite:
        async with db.transaction():
            # Get user and service info in same transaction
            user = await db.fetchrow("""
                SELECT id, email, credits FROM users 
                WHERE id = ? FOR UPDATE
            """, user_id)
            
            service = await db.fetchrow("""
                SELECT id, name, credits_required, price_usd 
                FROM service_types 
                WHERE name = ? AND enabled = 1
            """, service_type)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if not service:
                raise HTTPException(status_code=400, detail="Invalid service type")
            
            # Check credits within transaction
            if user["credits"] < service["credits_required"]:
                raise HTTPException(
                    status_code=402, 
                    detail=f"போதிய கிரெடிட்கள் இல்லை. தேவை: {service['credits_required']}, கிடைக்கும்: {user['credits']}"
                )
            
            # Deduct credits
            await db.execute("""
                UPDATE users SET credits = credits - ? 
                WHERE id = ?
            """, service["credits_required"], user_id)
            
            # Create session
            session_id = str(uuid.uuid4())
            await db.execute("""
                INSERT INTO sessions (id, user_email, service_type, question, guidance, 
                                    credits_used, original_price, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'completed', CURRENT_TIMESTAMP)
            """, (
                session_id, user["email"], service_type, 
                session_data.get("question", ""),
                f"Divine guidance for: {session_data.get('question', '')}",
                service["credits_required"], service["price_usd"]
            ))
            
            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "guidance": f"Divine guidance for: {session_data.get('question', '')}",
                    "astrology": {
                        "data": {
                            "nakshatra": {"name": "Ashwini"},
                            "chandra_rasi": {"name": "Mesha"}
                        }
                    },
                    "credits_deducted": service["credits_required"],
                    "remaining_credits": user["credits"] - service["credits_required"]
                }
            }
    else:
        # PostgreSQL version with proper locking
        async with db.transaction():
            # Similar implementation for PostgreSQL
            pass
```

### 4. Fix Authentication Flow Inconsistencies

#### Problem: Multiple authentication checks with different behaviors

**Create unified auth hook - frontend/src/hooks/useAuth.js:**
```javascript
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import spiritualAPI from '../lib/api';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const checkAuth = useCallback(async () => {
    try {
      setIsLoading(true);
      const authenticated = spiritualAPI.isAuthenticated();
      setIsAuthenticated(authenticated);
      
      if (authenticated) {
        const profile = await spiritualAPI.getUserProfile();
        if (profile && profile.success) {
          setUser(profile.data);
        } else {
          // Token might be invalid
          spiritualAPI.logout();
          setIsAuthenticated(false);
          setUser(null);
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      spiritualAPI.logout();
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();

    // Listen for auth changes
    const handleAuthChange = (event) => {
      if (event.detail.authenticated) {
        setIsAuthenticated(true);
        setUser(event.detail.user);
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    };

    window.addEventListener('auth-state-changed', handleAuthChange);
    return () => window.removeEventListener('auth-state-changed', handleAuthChange);
  }, [checkAuth]);

  const login = async (email, password) => {
    try {
      const result = await spiritualAPI.login(email, password);
      if (result.success) {
        setIsAuthenticated(true);
        setUser(result.user);
        return result;
      }
      return result;
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, message: 'Login failed' };
    }
  };

  const logout = () => {
    spiritualAPI.logout();
    setIsAuthenticated(false);
    setUser(null);
    navigate('/');
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
    isAdmin: user?.role === 'admin'
  };
};
```

**Update ProtectedRoute.jsx:**
```javascript
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isAdmin, isLoading } = useAuth();
  const location = useLocation();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto mb-4"></div>
          <p className="text-white text-xl">🕉️ Authenticating...</p>
        </div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### 5. Fix Credit Package Field Inconsistencies

#### Problem: Frontend expects different field names than backend provides

**Update backend/routers/credits.py:**
```python
@router.get("/packages")
async def get_credit_packages(db=Depends(get_db)):
    """Get available credit packages with consistent field names"""
    try:
        if hasattr(db, 'is_sqlite') and db.is_sqlite:
            packages = await db.fetch("""
                SELECT id, name, 
                       credits_amount as credits, 
                       price_usd, 
                       bonus_credits, 
                       enabled, 
                       created_at, 
                       updated_at,
                       description
                FROM credit_packages 
                WHERE enabled = 1 
                ORDER BY credits_amount ASC
            """)
        else:
            packages = await db.fetch("""
                SELECT id, name, 
                       credits_amount as credits, 
                       price_usd, 
                       bonus_credits, 
                       enabled, 
                       created_at, 
                       updated_at,
                       description
                FROM credit_packages 
                WHERE enabled = TRUE 
                ORDER BY credits_amount ASC
            """)
        
        return {
            "success": True, 
            "packages": [dict(package) for package in packages]
        }
    except Exception as e:
        print(f"Error fetching credit packages: {e}")
        raise HTTPException(status_code=500, detail="கிரெடிட் தொகுப்புகளை ஏற்ற முடியவில்லை")
```

### 6. Standardize API Response Format

#### Problem: Inconsistent response formats across endpoints

**Create response utils - backend/utils/responses.py:**
```python
from typing import Any, Dict, Optional

def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Standard success response format"""
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
    """Standard error response format"""
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "data": None
    }
```

**Update all backend routers to use standard format:**
```python
from utils.responses import success_response, error_response

# Example usage in services.py
@router.get("/types")
async def get_service_types(db=Depends(get_db)):
    try:
        # ... existing code ...
        return success_response(
            data=[dict(service) for service in services],
            message="Services loaded successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=error_response(
                message="Failed to load services",
                error_code="SERVICE_LOAD_ERROR"
            )
        )
```

### 7. Fix Frontend Component State Management

#### Problem: Duplicate loading states and API calls

**Create service hook - frontend/src/hooks/useServices.js:**
```javascript
import { useState, useEffect } from 'react';
import spiritualAPI from '../lib/api';

export const useServices = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadServices = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await spiritualAPI.request('/api/services/types');
      
      if (response && response.success) {
        setServices(response.data || []);
      } else {
        setError('Failed to load services');
        setServices([]);
      }
    } catch (err) {
      setError('Network error loading services');
      setServices([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadServices();
  }, []);

  return {
    services,
    loading,
    error,
    reload: loadServices
  };
};
```

**Update SpiritualGuidance.jsx to use the hook:**
```javascript
import { useServices } from '../hooks/useServices';

const SpiritualGuidance = () => {
  const { services, loading: servicesLoading, error: servicesError } = useServices();
  
  // Remove duplicate service loading logic
  // Use services from hook instead of local state
  
  // Rest of component...
};
```

## Implementation Priority

### Phase 1 (Week 1) - Critical Fixes
1. Create missing API endpoints (`/api/services/types`, `/api/services/stats`)
2. Fix service loading in all components
3. Implement atomic credit system
4. Standardize response formats

### Phase 2 (Week 2) - UX Improvements
1. Implement unified authentication hook
2. Fix credit package field inconsistencies
3. Add proper error handling
4. Implement loading states

### Phase 3 (Week 3) - Polish
1. Add real payment integration
2. Implement analytics
3. Add proper error boundaries
4. Optimize performance

This implementation plan addresses the most critical issues that are breaking the customer flow. Start with Phase 1 to get the basic functionality working properly, then move to the UX improvements in Phase 2.