"""
================================================================================
Farm Management System - Inventory Integration Helper
================================================================================
Version: 1.0.0
Last Updated: 2025-11-18

Description:
-----------
Helper service for integrating other modules (e.g., biofloc) with the inventory
module. Provides convenient methods for common inventory operations including:
- Stock deduction with module tracking
- Stock level checks
- Low stock alerts
- Consumption reporting
- Item lookups

This module is designed to be used by other business modules that need to
interact with inventory without directly calling the inventory service.

Usage:
------
from app.helpers.inventory_integration import InventoryIntegration

# Initialize with module name
inv = InventoryIntegration(module_name="biofloc")

# Deduct stock for a feeding operation
result = await inv.deduct_stock(
    item_sku="FEED-001",
    quantity=10.5,
    reference_id="tank-uuid",
    notes="Daily feeding for Tank A"
)

================================================================================
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from fastapi import HTTPException
import logging

from app.database import fetch_one, fetch_all, execute_query, DatabaseTransaction
from app.services import inventory_service

logger = logging.getLogger(__name__)


class InventoryIntegration:
    """
    Helper class for integrating modules with inventory system.

    Provides simplified methods for common inventory operations with
    automatic module reference tracking.
    """

    def __init__(self, module_name: str):
        """
        Initialize inventory integration helper.

        Args:
            module_name: Name of the module using inventory (e.g., "biofloc")
        """
        self.module_name = module_name
        logger.info(f"Initialized InventoryIntegration for module: {module_name}")

    # ========================================================================
    # STOCK DEDUCTION METHODS
    # ========================================================================

    async def deduct_stock(
        self,
        item_sku: str,
        quantity: float,
        user_id: str,
        reference_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deduct stock using FIFO logic with module tracking.

        Args:
            item_sku: SKU of the item to deduct
            quantity: Amount to deduct
            user_id: UUID of user performing the operation
            reference_id: Optional reference (e.g., tank_id, batch_id)
            notes: Optional notes about the operation

        Returns:
            Dict containing:
                - success: bool
                - batches_used: List of batches deducted from
                - total_cost: Decimal
                - avg_cost: Decimal
                - new_balance: Decimal

        Raises:
            HTTPException: If item not found or insufficient stock
        """
        try:
            # 1. Get item by SKU
            item = await self._get_item_by_sku(item_sku)
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item with SKU '{item_sku}' not found"
                )

            # 2. Use inventory service to deduct stock
            result = await inventory_service.use_stock_fifo(
                item_id=item["id"],
                quantity=Decimal(str(quantity)),
                user_id=user_id,
                module_reference=self.module_name,
                tank_id=reference_id,  # Generic reference field
                notes=notes or f"{self.module_name} stock deduction"
            )

            logger.info(
                f"Stock deducted: {quantity} {item['unit']} of {item_sku} "
                f"for {self.module_name} (ref: {reference_id})"
            )

            return {
                "success": True,
                "item_name": item["item_name"],
                "sku": item_sku,
                "quantity_deducted": float(quantity),
                "unit": item["unit"],
                "batches_used": result["batches_used"],
                "total_cost": float(result["total_cost"]),
                "avg_cost": float(result["avg_cost"]),
                "new_balance": float(result["new_balance"])
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deducting stock: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to deduct stock: {str(e)}"
            )

    async def deduct_multiple_items(
        self,
        items: List[Dict[str, Any]],
        user_id: str,
        reference_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deduct multiple items in sequence (e.g., for a feeding schedule).

        Note: This is NOT atomic - each item is deducted separately.
        If one fails, previous deductions are NOT rolled back.

        Args:
            items: List of dicts with 'sku' and 'quantity' keys
            user_id: UUID of user performing the operation
            reference_id: Optional reference (e.g., tank_id)
            notes: Optional notes for all items

        Returns:
            Dict containing:
                - total_items: int
                - successful: int
                - failed: int
                - results: List of individual results
                - total_cost: float

        Example:
            items = [
                {"sku": "FEED-001", "quantity": 10.5},
                {"sku": "CHEM-002", "quantity": 2.0}
            ]
        """
        results = []
        successful = 0
        failed = 0
        total_cost = 0.0

        for item_data in items:
            try:
                result = await self.deduct_stock(
                    item_sku=item_data["sku"],
                    quantity=item_data["quantity"],
                    user_id=user_id,
                    reference_id=reference_id,
                    notes=notes or item_data.get("notes")
                )
                results.append({
                    "sku": item_data["sku"],
                    "status": "success",
                    "result": result
                })
                successful += 1
                total_cost += result["total_cost"]

            except Exception as e:
                results.append({
                    "sku": item_data["sku"],
                    "status": "failed",
                    "error": str(e)
                })
                failed += 1
                logger.error(f"Failed to deduct {item_data['sku']}: {str(e)}")

        return {
            "total_items": len(items),
            "successful": successful,
            "failed": failed,
            "results": results,
            "total_cost": total_cost
        }

    # ========================================================================
    # STOCK LEVEL CHECKING METHODS
    # ========================================================================

    async def check_stock_level(self, item_sku: str) -> Dict[str, Any]:
        """
        Check current stock level for an item.

        Args:
            item_sku: SKU of the item

        Returns:
            Dict containing current stock info
        """
        item = await self._get_item_by_sku(item_sku)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with SKU '{item_sku}' not found"
            )

        return {
            "sku": item_sku,
            "item_name": item["item_name"],
            "current_qty": float(item["current_qty"]),
            "unit": item["unit"],
            "reorder_threshold": float(item["reorder_threshold"]),
            "min_stock_level": float(item["min_stock_level"]),
            "is_low_stock": item["current_qty"] <= item["reorder_threshold"],
            "deficit": float(max(0, item["reorder_threshold"] - item["current_qty"]))
        }

    async def check_multiple_stock_levels(
        self,
        item_skus: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Check stock levels for multiple items.

        Args:
            item_skus: List of SKUs

        Returns:
            List of stock level dicts
        """
        results = []
        for sku in item_skus:
            try:
                result = await self.check_stock_level(sku)
                results.append(result)
            except HTTPException as e:
                results.append({
                    "sku": sku,
                    "error": e.detail
                })
        return results

    async def is_stock_available(
        self,
        item_sku: str,
        required_quantity: float
    ) -> bool:
        """
        Check if sufficient stock is available for an item.

        Args:
            item_sku: SKU of the item
            required_quantity: Amount needed

        Returns:
            True if sufficient stock available, False otherwise
        """
        try:
            stock_info = await self.check_stock_level(item_sku)
            return stock_info["current_qty"] >= required_quantity
        except:
            return False

    # ========================================================================
    # ALERT METHODS
    # ========================================================================

    async def get_low_stock_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all items below reorder threshold.

        Returns:
            List of low stock items
        """
        try:
            alerts = await inventory_service.get_low_stock_alerts()
            return [
                {
                    "sku": item["sku"],
                    "item_name": item["item_name"],
                    "current_qty": float(item["current_qty"]),
                    "reorder_threshold": float(item["reorder_threshold"]),
                    "deficit": float(item["deficit"]),
                    "unit": item["unit"],
                    "category": item["category"]
                }
                for item in alerts
            ]
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {str(e)}")
            return []

    async def get_expiring_items(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get items expiring within specified days.

        Args:
            days: Number of days to check (default: 30)

        Returns:
            List of expiring items
        """
        try:
            alerts = await inventory_service.get_expiry_alerts(days=days)
            return [
                {
                    "sku": item["sku"],
                    "item_name": item["item_name"],
                    "batch_number": item["batch_number"],
                    "remaining_qty": float(item["remaining_qty"]),
                    "unit": item["unit"],
                    "expiry_date": str(item["expiry_date"]),
                    "days_until_expiry": item["days_until_expiry"]
                }
                for item in alerts
            ]
        except Exception as e:
            logger.error(f"Error getting expiry alerts: {str(e)}")
            return []

    # ========================================================================
    # REPORTING METHODS
    # ========================================================================

    async def get_consumption_report(
        self,
        start_date: date,
        end_date: date,
        item_sku: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get consumption report for the module within date range.

        Args:
            start_date: Start date for report
            end_date: End date for report
            item_sku: Optional filter by specific item
            reference_id: Optional filter by reference (e.g., tank_id)

        Returns:
            Dict containing consumption summary and details
        """
        try:
            # Build query
            query = """
                SELECT
                    im.sku,
                    im.item_name,
                    im.unit,
                    COUNT(*) as transaction_count,
                    SUM(ABS(it.quantity_change)) as total_quantity,
                    SUM(it.total_cost) as total_cost,
                    AVG(it.unit_cost) as avg_unit_cost
                FROM inventory_transactions it
                JOIN item_master im ON it.item_master_id = im.id
                WHERE it.transaction_type = 'use'
                    AND it.module_reference = $1
                    AND it.transaction_date >= $2
                    AND it.transaction_date <= $3
            """
            params = [self.module_name, start_date, end_date]
            param_count = 4

            # Add optional filters
            if item_sku:
                item = await self._get_item_by_sku(item_sku)
                if item:
                    query += f" AND it.item_master_id = ${param_count}"
                    params.append(item["id"])
                    param_count += 1

            if reference_id:
                query += f" AND it.tank_id = ${param_count}"
                params.append(reference_id)
                param_count += 1

            query += " GROUP BY im.sku, im.item_name, im.unit ORDER BY total_cost DESC"

            results = await fetch_all(query, *params)

            # Calculate totals
            total_cost = sum(float(row["total_cost"] or 0) for row in results)
            total_transactions = sum(int(row["transaction_count"]) for row in results)

            return {
                "module": self.module_name,
                "period": {
                    "start_date": str(start_date),
                    "end_date": str(end_date)
                },
                "summary": {
                    "total_items": len(results),
                    "total_transactions": total_transactions,
                    "total_cost": total_cost
                },
                "items": [
                    {
                        "sku": row["sku"],
                        "item_name": row["item_name"],
                        "unit": row["unit"],
                        "quantity_consumed": float(row["total_quantity"]),
                        "transaction_count": int(row["transaction_count"]),
                        "total_cost": float(row["total_cost"] or 0),
                        "avg_unit_cost": float(row["avg_unit_cost"] or 0)
                    }
                    for row in results
                ]
            }

        except Exception as e:
            logger.error(f"Error generating consumption report: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate report: {str(e)}"
            )

    async def get_detailed_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        item_sku: Optional[str] = None,
        reference_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get detailed transaction history for the module.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            item_sku: Optional SKU filter
            reference_id: Optional reference filter
            limit: Maximum number of transactions to return

        Returns:
            List of transaction details
        """
        try:
            query = """
                SELECT
                    it.transaction_date,
                    im.sku,
                    im.item_name,
                    im.unit,
                    it.batch_number,
                    ABS(it.quantity_change) as quantity,
                    it.unit_cost,
                    it.total_cost,
                    it.new_balance,
                    it.tank_id as reference_id,
                    it.notes,
                    u.full_name as user_name
                FROM inventory_transactions it
                JOIN item_master im ON it.item_master_id = im.id
                LEFT JOIN users u ON it.user_id = u.id
                WHERE it.transaction_type = 'use'
                    AND it.module_reference = $1
            """
            params = [self.module_name]
            param_count = 2

            if start_date:
                query += f" AND it.transaction_date >= ${param_count}"
                params.append(start_date)
                param_count += 1

            if end_date:
                query += f" AND it.transaction_date <= ${param_count}"
                params.append(end_date)
                param_count += 1

            if item_sku:
                item = await self._get_item_by_sku(item_sku)
                if item:
                    query += f" AND it.item_master_id = ${param_count}"
                    params.append(item["id"])
                    param_count += 1

            if reference_id:
                query += f" AND it.tank_id = ${param_count}"
                params.append(reference_id)
                param_count += 1

            query += f" ORDER BY it.transaction_date DESC LIMIT ${param_count}"
            params.append(limit)

            results = await fetch_all(query, *params)

            return [
                {
                    "transaction_date": row["transaction_date"].isoformat(),
                    "sku": row["sku"],
                    "item_name": row["item_name"],
                    "quantity": float(row["quantity"]),
                    "unit": row["unit"],
                    "batch_number": row["batch_number"],
                    "unit_cost": float(row["unit_cost"] or 0),
                    "total_cost": float(row["total_cost"] or 0),
                    "new_balance": float(row["new_balance"] or 0),
                    "reference_id": row["reference_id"],
                    "notes": row["notes"],
                    "user_name": row["user_name"]
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting transaction details: {str(e)}")
            return []

    # ========================================================================
    # ITEM LOOKUP METHODS
    # ========================================================================

    async def get_item_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Get item details by SKU.

        Args:
            sku: Item SKU

        Returns:
            Item details or None if not found
        """
        item = await self._get_item_by_sku(sku)
        if not item:
            return None

        return {
            "id": str(item["id"]),
            "sku": item["sku"],
            "item_name": item["item_name"],
            "category": item["category"],
            "unit": item["unit"],
            "current_qty": float(item["current_qty"]),
            "reorder_threshold": float(item["reorder_threshold"]),
            "min_stock_level": float(item["min_stock_level"]),
            "is_active": item["is_active"]
        }

    async def get_items_by_category(
        self,
        category: str
    ) -> List[Dict[str, Any]]:
        """
        Get all items in a category.

        Args:
            category: Category name (e.g., "Feed", "Chemicals")

        Returns:
            List of items in category
        """
        try:
            query = """
                SELECT id, sku, item_name, category, unit,
                       current_qty, reorder_threshold, min_stock_level, is_active
                FROM item_master
                WHERE category = $1 AND is_active = true
                ORDER BY item_name
            """
            results = await fetch_all(query, category)

            return [
                {
                    "id": str(row["id"]),
                    "sku": row["sku"],
                    "item_name": row["item_name"],
                    "category": row["category"],
                    "unit": row["unit"],
                    "current_qty": float(row["current_qty"]),
                    "reorder_threshold": float(row["reorder_threshold"]),
                    "min_stock_level": float(row["min_stock_level"])
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting items by category: {str(e)}")
            return []

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    async def _get_item_by_sku(self, sku: str) -> Optional[Dict]:
        """Internal helper to get item by SKU."""
        query = """
            SELECT id, sku, item_name, category, unit,
                   current_qty, reorder_threshold, min_stock_level, is_active
            FROM item_master
            WHERE sku = $1
        """
        return await fetch_one(query, sku)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_inventory_integration(module_name: str) -> InventoryIntegration:
    """
    Factory function to create an InventoryIntegration instance.

    Args:
        module_name: Name of the module (e.g., "biofloc")

    Returns:
        InventoryIntegration instance
    """
    return InventoryIntegration(module_name=module_name)
