from fastapi import APIRouter, Request, Depends, HTTPException
from db import get_db
import os
from datetime import datetime

# Import centralized JWT handler
from auth.jwt_config import JWTHandler

router = APIRouter(prefix="/api/credits", tags=["Credits"])

def get_user_id_from_token(request: Request) -> str:
    """Extract user ID from JWT token using centralized handler"""
    try:
        return JWTHandler.get_user_id_from_token(request)
    except HTTPException as e:
        # Convert to Tamil error messages
        if e.status_code == 401:
            raise HTTPException(status_code=401, detail="அங்கீகாரம் தேவை - தயவுசெய்து மீண்டும் உள்நுழையவும்")
        raise e

def convert_user_id_to_int(user_id: str) -> int | None:
    """Convert string user_id to integer for database queries"""
    if not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
        return None

@router.post("/purchase")
async def purchase_credits(request: Request, db=Depends(get_db)):
    """Purchase credits with bonus credits for larger packages"""
    try:
        user_id = get_user_id_from_token(request)
        user_id_int = convert_user_id_to_int(user_id)
        if user_id_int is None:
            raise HTTPException(status_code=400, detail="தவறான பயனர் அடையாளம்")
        
        data = await request.json()
        
        package_id = data.get("package_id")
        if not package_id:
            raise HTTPException(status_code=400, detail="கிரெடிட் தொகுப்பு தேர்வு தேவை")
        
        # Get credit package details
        package = await db.fetchrow(
            "SELECT id, name, credits, price_usd, bonus_credits FROM credit_packages WHERE id = $1 AND enabled = TRUE",
            package_id
        )
        
        if not package:
            raise HTTPException(status_code=400, detail="தவறான கிரெடிட் தொகுப்பு - தயவுசெய்து மீண்டும் முயற்சிக்கவும்")
        
        # Validate credit amounts
        base_credits = int(package["credits"])
        bonus_credits = int(package["bonus_credits"] or 0)
        
        if base_credits <= 0:
            raise HTTPException(status_code=400, detail="தவறான கிரெடிட் அளவு")
        
        # Calculate total credits (base + bonus)
        total_credits = base_credits + bonus_credits
        
        # TODO: Integrate with actual payment processor (Stripe, etc.)
        # For now, simulate successful payment
        
        # Add credits to user account with proper transaction
        async with db.transaction():
            # Update user credits
            await db.execute(
                "UPDATE users SET credits = credits + $1 WHERE id = $2",
                total_credits, user_id_int
            )
            
            # Record the transaction
            await db.execute("""
                INSERT INTO credit_transactions (user_id, package_id, credits_purchased, bonus_credits, total_credits, amount_usd, status, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, 'completed', NOW())
            """, user_id_int, package_id, base_credits, bonus_credits, total_credits, package["price_usd"])
        
        return {
            "success": True, 
            "message": f"வெற்றிகரமாக {total_credits} கிரெடிட்கள் வாங்கப்பட்டன",
            "data": {
                "credits_purchased": base_credits,
                "bonus_credits": bonus_credits,
                "total_credits": total_credits,
                "amount_usd": package["price_usd"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Credit purchase error: {e}")
        raise HTTPException(status_code=500, detail="கிரெடிட் வாங்குதல் தோல்வி - தயவுசெய்து மீண்டும் முயற்சிக்கவும்")

@router.get("/packages")
async def get_credit_packages(db=Depends(get_db)):
    """Get available credit packages"""
    try:
        packages = await db.fetch(
            "SELECT id, name, credits_amount, price_usd, bonus_credits, enabled, created_at, updated_at FROM credit_packages WHERE enabled = TRUE ORDER BY credits_amount ASC"
        )
        return {"success": True, "packages": packages}
    except Exception as e:
        print(f"Error fetching credit packages: {e}")
        raise HTTPException(status_code=500, detail="கிரெடிட் தொகுப்புகளை ஏற்ற முடியவில்லை") 