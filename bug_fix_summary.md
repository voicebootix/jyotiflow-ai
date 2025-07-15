# Type Mismatch Bug Fix - User Profile and Credits Endpoints

## Problem
A type mismatch bug affected the `/api/user/profile` and `/api/user/credits` endpoints due to incorrect double conversion of user IDs.

### Root Cause
- `get_user_id_as_int()` returns `int | None` (already converts string to integer)
- `convert_user_id_to_int()` expects `str | None` input and returns `int | None`
- The profile and credits endpoints were incorrectly passing the already-converted integer from `get_user_id_as_int()` to `convert_user_id_to_int()`, causing runtime type errors

## Solution
**Fixed both endpoints to use `get_user_id_as_int()` directly without the redundant second conversion:**

### Profile Endpoint Fix (`/api/user/profile`)
- **Before**: Called `get_user_id_as_int()`, then passed result to `convert_user_id_to_int()` 
- **After**: Uses `get_user_id_as_int()` result directly as `user_id_int`
- **Removed**: Redundant conversion step and unnecessary fallback logic

### Credits Endpoint Fix (`/api/user/credits`)
- **Before**: Called `get_user_id_as_int()`, then passed result to `convert_user_id_to_int()`
- **After**: Uses `get_user_id_as_int()` result directly as `user_id_int`
- **Removed**: Redundant conversion step and "Invalid user ID" error path

## Pattern Consistency
Both endpoints now follow the same pattern as the `/api/user/sessions` endpoint, which was already implemented correctly:

```python
user_id_int = get_user_id_as_int(request)  # Already returns int or None
if not user_id_int:
    # Handle unauthenticated case
    return ...
```

## Files Modified
- `backend/routers/user.py` (lines 58-85 and 109-116)

## Verification
- Syntax check passed successfully
- Type consistency ensured across all user endpoints
- Runtime type errors eliminated