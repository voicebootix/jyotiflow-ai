"""
Unified Credit Package Service
Consolidates all credit package logic into a single, consistent service
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class CreditPackageService:
    """Unified service for credit package operations"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_public_packages(self) -> Dict[str, Any]:
        """Get credit packages for public customers with dynamic pricing"""
        try:
            packages = await self.db.fetch("""
                SELECT 
                    id, 
                    name, 
                    credits_amount as credits, 
                    price_usd, 
                    COALESCE(bonus_credits, 0) as bonus_credits, 
                    COALESCE(enabled, true) as enabled, 
                    COALESCE(description, '') as description,
                    created_at, 
                    updated_at
                FROM credit_packages 
                WHERE COALESCE(enabled, true) = TRUE 
                ORDER BY credits_amount ASC
            """)
            
            # Apply dynamic pricing
            pricing_config = await self._get_dynamic_pricing()
            
            result = []
            for package in packages:
                package_dict = dict(package)
                
                # Apply dynamic pricing
                original_price = float(package_dict['price_usd'])
                package_dict['price_usd'] = round(original_price * pricing_config['multiplier'], 2)
                
                # Add pricing metadata
                package_dict['pricing_info'] = {
                    'is_dynamic': True,
                    'original_price': original_price,
                    'multiplier_applied': pricing_config['multiplier']
                }
                
                result.append(package_dict)
            
            return {
                "success": True, 
                "data": result,
                "pricing_config": {
                    "dynamic_pricing_enabled": True,
                    "last_updated": "now",
                    "multiplier": pricing_config['multiplier']
                }
            }
        except Exception as e:
            logger.error(f"Error fetching credit packages: {e}")
            # Return empty result instead of hardcoded packages
            return {
                "success": True,
                "data": [],
                "pricing_config": {
                    "dynamic_pricing_enabled": False,
                    "last_updated": "now",
                    "multiplier": 1.0
                },
                "message": "No credit packages available. Please contact admin to configure packages."
            }
    
    async def get_admin_packages(self) -> List[Dict[str, Any]]:
        """Get credit packages for admin management"""
        try:
            result = await self.db.fetch("""
                SELECT 
                    id, 
                    name, 
                    credits_amount, 
                    price_usd, 
                    COALESCE(bonus_credits, 0) as bonus_credits, 
                    COALESCE(enabled, true) as enabled,
                    COALESCE(description, '') as description,
                    stripe_product_id, 
                    stripe_price_id,
                    created_at, 
                    updated_at
                FROM credit_packages 
                ORDER BY credits_amount ASC
            """)
            
            return [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "credits_amount": row["credits_amount"],
                    "price_usd": float(row["price_usd"]),
                    "bonus_credits": row["bonus_credits"],
                    "enabled": row["enabled"],
                    "description": row["description"],
                    "stripe_product_id": row["stripe_product_id"],
                    "stripe_price_id": row["stripe_price_id"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error fetching admin credit packages: {e}")
            return []
    
    async def create_package(self, package_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new credit package"""
        try:
            package_id = str(uuid.uuid4())
            
            await self.db.execute("""
                INSERT INTO credit_packages (
                    id, name, credits_amount, price_usd, bonus_credits, 
                    description, enabled, stripe_product_id, stripe_price_id, 
                    created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            """, 
                package_id,
                package_data.get("name"),
                int(package_data.get("credits_amount", 0)),
                float(package_data.get("price_usd", 0)),
                int(package_data.get("bonus_credits", 0)),
                package_data.get("description", ""),
                package_data.get("enabled", True),
                package_data.get("stripe_product_id"),
                package_data.get("stripe_price_id")
            )
            
            return {"success": True, "package_id": package_id}
        except Exception as e:
            logger.error(f"Error creating credit package: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_package(self, package_id: str, package_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing credit package"""
        try:
            result = await self.db.execute("""
                UPDATE credit_packages 
                SET 
                    name = $1, 
                    credits_amount = $2, 
                    price_usd = $3, 
                    bonus_credits = $4,
                    description = $5,
                    enabled = $6, 
                    stripe_product_id = $7, 
                    stripe_price_id = $8, 
                    updated_at = NOW()
                WHERE id = $9
            """,
                package_data.get("name"),
                int(package_data.get("credits_amount", 0)),
                float(package_data.get("price_usd", 0)),
                int(package_data.get("bonus_credits", 0)),
                package_data.get("description", ""),
                package_data.get("enabled", True),
                package_data.get("stripe_product_id"),
                package_data.get("stripe_price_id"),
                package_id
            )
            
            if result == "UPDATE 0":
                return {"success": False, "error": "Credit package not found"}
            
            return {"success": True}
        except Exception as e:
            logger.error(f"Error updating credit package: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_package(self, package_id: str) -> Dict[str, Any]:
        """Soft delete a credit package (disable it)"""
        try:
            result = await self.db.execute("""
                UPDATE credit_packages 
                SET enabled = FALSE, updated_at = NOW()
                WHERE id = $1
            """, package_id)
            
            if result == "UPDATE 0":
                return {"success": False, "error": "Credit package not found"}
            
            return {"success": True}
        except Exception as e:
            logger.error(f"Error deleting credit package: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_package_by_id(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific credit package by ID"""
        try:
            row = await self.db.fetchrow("""
                SELECT 
                    id, name, credits_amount, price_usd, bonus_credits,
                    enabled, description, stripe_product_id, stripe_price_id,
                    created_at, updated_at
                FROM credit_packages 
                WHERE id = $1
            """, package_id)
            
            if row:
                return {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "credits_amount": row["credits_amount"],
                    "price_usd": float(row["price_usd"]),
                    "bonus_credits": row["bonus_credits"],
                    "enabled": row["enabled"],
                    "description": row["description"],
                    "stripe_product_id": row["stripe_product_id"],
                    "stripe_price_id": row["stripe_price_id"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching credit package by ID: {e}")
            return None
    
    async def purchase_credits(self, user_id: str, package_id: str) -> Dict[str, Any]:
        """Purchase credits for a user"""
        try:
            # Get package details
            package = await self.get_package_by_id(package_id)
            if not package or not package["enabled"]:
                return {"success": False, "error": "Invalid or disabled credit package"}
            
            # Calculate total credits
            base_credits = int(package["credits_amount"])
            bonus_credits = int(package["bonus_credits"] or 0)
            total_credits = base_credits + bonus_credits
            
            if base_credits <= 0:
                return {"success": False, "error": "Invalid credit amount"}
            
            # TODO: Integrate with actual payment processor (Stripe, etc.)
            # For now, simulate successful payment
            
            # Add credits to user account
            async with self.db.transaction():
                # Update user credits
                await self.db.execute("""
                    UPDATE users SET credits = credits + $1 WHERE id = $2
                """, total_credits, user_id)
                
                # Record the transaction
                await self.db.execute("""
                    INSERT INTO credit_transactions (
                        user_id, package_id, credits_purchased, bonus_credits, 
                        total_credits, amount_usd, status, created_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, 'completed', NOW())
                """, user_id, package_id, base_credits, bonus_credits, total_credits, package["price_usd"])
            
            return {
                "success": True,
                "message": f"Successfully purchased {total_credits} credits",
                "data": {
                    "credits_purchased": base_credits,
                    "bonus_credits": bonus_credits,
                    "total_credits": total_credits,
                    "amount_usd": package["price_usd"]
                }
            }
        except Exception as e:
            logger.error(f"Error purchasing credits: {e}")
            return {"success": False, "error": "Credit purchase failed"}
    
    async def _get_dynamic_pricing(self) -> Dict[str, Any]:
        """Get dynamic pricing configuration"""
        try:
            # Get global pricing multiplier
            pricing_multiplier = await self.db.fetchrow("""
                SELECT value FROM platform_settings 
                WHERE key = 'pricing_multiplier'
            """)
            
            multiplier = 1.0
            if pricing_multiplier and pricing_multiplier['value']:
                multiplier = float(pricing_multiplier['value'].get('multiplier', 1.0))
            
            return {'multiplier': multiplier}
        except Exception as e:
            logger.warning(f"Dynamic pricing error: {e}")
            return {'multiplier': 1.0} 