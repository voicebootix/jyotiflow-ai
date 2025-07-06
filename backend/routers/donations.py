from fastapi import APIRouter, Depends, HTTPException, Body, Request
from typing import List, Optional, Dict, Any
import stripe
from datetime import datetime, timezone
import os
import uuid

from db import get_db
from deps import get_current_user

router = APIRouter(prefix="/api/donations", tags=["donations"])

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/process")
async def process_donation(request: Request, db=Depends(get_db)):
    """Process a donation payment"""
    try:
        data = await request.json()
        donation_id = data.get("donation_id")
        amount_usd = data.get("amount_usd")
        message = data.get("message", "")
        session_id = data.get("session_id")
        
        if not donation_id or not amount_usd:
            raise HTTPException(status_code=400, detail="தான விவரங்கள் தேவை")
        
        # Get donation details
        if hasattr(db, 'is_sqlite') and db.is_sqlite:
            donation = await db.fetchrow(
                "SELECT id, name, tamil_name, price_usd, icon FROM donations WHERE id = ? AND enabled = 1",
                donation_id
            )
        else:
            donation = await db.fetchrow(
                "SELECT id, name, tamil_name, price_usd, icon FROM donations WHERE id = $1 AND enabled = TRUE",
                donation_id
            )
        
        if not donation:
            raise HTTPException(status_code=404, detail="தானம் கிடைக்கவில்லை")
        
        # TODO: Integrate with actual payment processor (Stripe, etc.)
        # For now, simulate successful payment
        payment_intent_id = f"pi_{uuid.uuid4().hex[:24]}"
        
        # Record the transaction
        if hasattr(db, 'is_sqlite') and db.is_sqlite:
            await db.execute("""
                INSERT INTO donation_transactions (donation_id, amount_usd, message, session_id, payment_intent_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'completed', CURRENT_TIMESTAMP)
            """, donation_id, amount_usd, message, session_id, payment_intent_id)
        else:
            await db.execute("""
                INSERT INTO donation_transactions (donation_id, amount_usd, message, session_id, payment_intent_id, status, created_at)
                VALUES ($1, $2, $3, $4, $5, 'completed', NOW())
            """, donation_id, amount_usd, message, session_id, payment_intent_id)
        
        return {
            "success": True,
            "message": "தானம் வெற்றிகரமாக செயல்படுத்தப்பட்டது",
            "payment_intent_id": payment_intent_id,
            "donation": {
                "id": donation["id"],
                "name": donation["name"],
                "tamil_name": donation["tamil_name"],
                "amount_usd": amount_usd
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Donation processing error: {e}")
        raise HTTPException(status_code=500, detail="தானம் செயல்படுத்த முடியவில்லை")

@router.post("/confirm")
async def confirm_donation(
    payment_intent_id: str = Body(..., embed=True),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_db)
):
    """Confirm a donation payment"""
    try:
        # Verify payment intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status != "succeeded":
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Update transaction status
        result = await db.execute("""
            UPDATE donation_transactions 
            SET status = $1, completed_at = NOW(), updated_at = NOW()
            WHERE stripe_payment_intent_id = $2 AND user_id = $3
        """, "completed", payment_intent_id, current_user["id"])
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Get transaction details
        transaction = await db.fetchrow("""
            SELECT dt.*, d.name, d.tamil_name, d.icon
            FROM donation_transactions dt
            JOIN donations d ON dt.donation_id = d.id
            WHERE dt.stripe_payment_intent_id = $1
        """, payment_intent_id)
        
        # Update donation analytics
        await update_donation_analytics(db, transaction["donation_id"])
        
        return {
            "success": True,
            "message": "Donation confirmed successfully",
            "transaction": {
                "id": str(transaction["id"]),
                "amount_usd": float(transaction["amount_usd"]),
                "donation_name": transaction["name"],
                "tamil_name": transaction["tamil_name"],
                "icon": transaction["icon"],
                "completed_at": transaction["completed_at"].isoformat() if transaction["completed_at"] else None
            }
        }
        
    except Exception as e:
        print(f"Donation confirmation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm donation")

@router.get("/history")
async def get_donation_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's donation history"""
    try:
        transactions = await db.fetch("""
            SELECT dt.*, d.name, d.tamil_name, d.icon, d.category
            FROM donation_transactions dt
            JOIN donations d ON dt.donation_id = d.id
            WHERE dt.user_id = $1
            ORDER BY dt.created_at DESC
            LIMIT 50
        """, current_user["id"])
        
        return {
            "success": True,
            "transactions": [
                {
                    "id": str(t["id"]),
                    "amount_usd": float(t["amount_usd"]),
                    "donation_name": t["name"],
                    "tamil_name": t["tamil_name"],
                    "icon": t["icon"],
                    "category": t["category"],
                    "status": t["status"],
                    "message": t["message"],
                    "created_at": t["created_at"].isoformat(),
                    "completed_at": t["completed_at"].isoformat() if t["completed_at"] else None
                }
                for t in transactions
            ]
        }
        
    except Exception as e:
        print(f"Donation history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get donation history")

@router.get("/analytics")
async def get_donation_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get donation analytics for admin"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get recent donation analytics
        analytics = await db.fetch("""
            SELECT 
                da.date,
                d.name,
                d.tamil_name,
                d.icon,
                da.total_transactions,
                da.total_amount_usd,
                da.successful_transactions,
                da.unique_donors
            FROM donation_analytics da
            JOIN donations d ON da.donation_id = d.id
            WHERE da.date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY da.date DESC, da.total_amount_usd DESC
        """)
        
        # Get total donations summary
        summary = await db.fetchrow("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount_usd) as total_amount,
                COUNT(DISTINCT user_id) as unique_donors
            FROM donation_transactions 
            WHERE status = 'completed' 
            AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        """)
        
        return {
            "success": True,
            "analytics": [
                {
                    "date": a["date"].isoformat(),
                    "donation_name": a["name"],
                    "tamil_name": a["tamil_name"],
                    "icon": a["icon"],
                    "total_transactions": a["total_transactions"],
                    "total_amount_usd": float(a["total_amount_usd"]),
                    "successful_transactions": a["successful_transactions"],
                    "unique_donors": a["unique_donors"]
                }
                for a in analytics
            ],
            "summary": {
                "total_transactions": summary["total_transactions"] or 0,
                "total_amount_usd": float(summary["total_amount"] or 0),
                "unique_donors": summary["unique_donors"] or 0
            }
        }
        
    except Exception as e:
        print(f"Donation analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get donation analytics")

async def update_donation_analytics(db, donation_id: str):
    """Update donation analytics for a specific donation"""
    try:
        # Get today's analytics
        today = datetime.now(timezone.utc).date()
        
        # Get transaction data for today
        transactions = await db.fetch("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount_usd) as total_amount,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_transactions,
                COUNT(DISTINCT user_id) as unique_donors
            FROM donation_transactions 
            WHERE donation_id = $1 
            AND DATE(created_at) = $2
        """, donation_id, today)
        
        if transactions:
            t = transactions[0]
            total_amount = float(t["total_amount"] or 0)
            total_transactions = t["total_transactions"] or 0
            avg_amount = total_amount / total_transactions if total_transactions > 0 else 0
            
            # Upsert analytics
            await db.execute("""
                INSERT INTO donation_analytics (
                    date, donation_id, total_transactions, total_amount_usd,
                    successful_transactions, unique_donors, average_amount_usd
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (date, donation_id) DO UPDATE SET
                    total_transactions = EXCLUDED.total_transactions,
                    total_amount_usd = EXCLUDED.total_amount_usd,
                    successful_transactions = EXCLUDED.successful_transactions,
                    unique_donors = EXCLUDED.unique_donors,
                    average_amount_usd = EXCLUDED.average_amount_usd,
                    updated_at = NOW()
            """, today, donation_id, total_transactions, total_amount,
                 t["successful_transactions"] or 0, t["unique_donors"] or 0, avg_amount)
    
    except Exception as e:
        print(f"Error updating donation analytics: {e}")

@router.get("/webhook")
async def stripe_webhook():
    """Handle Stripe webhook for donation confirmations"""
    # This would be implemented to handle Stripe webhooks
    # For now, we'll use the confirm endpoint directly
    pass 

@router.get("/session-total/{session_id}")
async def get_session_total_donations(session_id: str, db = Depends(get_db)):
    """Get total donations for a session"""
    try:
        if hasattr(db, 'is_sqlite') and db.is_sqlite:
            # Sum from session_donations if available, else fallback to donation_transactions
            total = await db.fetchval(
                "SELECT COALESCE(SUM(amount_usd), 0) FROM session_donations WHERE session_id = ?",
                session_id
            )
            if total == 0:
                # Fallback: sum from donation_transactions
                total = await db.fetchval(
                    "SELECT COALESCE(SUM(amount_usd), 0) FROM donation_transactions WHERE session_id = ? AND status = 'completed'",
                    session_id
                )
        else:
            # Sum from session_donations if available, else fallback to donation_transactions
            total = await db.fetchval(
                "SELECT COALESCE(SUM(amount_usd), 0) FROM session_donations WHERE session_id = $1",
                session_id
            )
            if total == 0:
                # Fallback: sum from donation_transactions
                total = await db.fetchval(
                    "SELECT COALESCE(SUM(amount_usd), 0) FROM donation_transactions WHERE session_id = $1 AND status = 'completed'",
                    session_id
                )
        return {"success": True, "session_id": session_id, "total_donations": float(total or 0)}
    except Exception as e:
        print(f"Error getting session total donations: {e}")
        return {"success": False, "total_donations": 0, "error": str(e)}

@router.get("/top-donors/monthly")
async def get_monthly_top_donors(db = Depends(get_db)):
    """Get top donors for the current month"""
    try:
        if hasattr(db, 'is_sqlite') and db.is_sqlite:
            # Get current month's top donors
            top_donors = await db.fetch("""
                SELECT 
                    u.email,
                    u.first_name,
                    u.last_name,
                    COALESCE(SUM(dt.amount_usd), 0) as total_donated,
                    COUNT(dt.id) as donation_count
                FROM users u
                LEFT JOIN donation_transactions dt ON u.id = dt.user_id 
                    AND dt.status = 'completed'
                    AND dt.created_at >= date('now', 'start of month')
                GROUP BY u.id, u.email, u.first_name, u.last_name
                HAVING COALESCE(SUM(dt.amount_usd), 0) > 0
                ORDER BY total_donated DESC
                LIMIT 10
            """)
        else:
            # Get current month's top donors
            top_donors = await db.fetch("""
                SELECT 
                    u.email,
                    u.first_name,
                    u.last_name,
                    COALESCE(SUM(dt.amount_usd), 0) as total_donated,
                    COUNT(dt.id) as donation_count
                FROM users u
                LEFT JOIN donation_transactions dt ON u.id = dt.user_id 
                    AND dt.status = 'completed'
                    AND dt.created_at >= date_trunc('month', CURRENT_DATE)
                GROUP BY u.id, u.email, u.first_name, u.last_name
                HAVING COALESCE(SUM(dt.amount_usd), 0) > 0
                ORDER BY total_donated DESC
                LIMIT 10
            """)
        
        return {
            "success": True, 
            "top_donors": [
                {
                    "name": f"{donor['first_name'] or 'Anonymous'} {donor['last_name'] or ''}".strip(),
                    "email": donor['email'],
                    "total_donated": float(donor['total_donated']),
                    "donation_count": donor['donation_count']
                }
                for donor in top_donors
            ]
        }
    except Exception as e:
        print(f"Error getting monthly top donors: {e}")
        return {"success": False, "top_donors": [], "error": str(e)} 