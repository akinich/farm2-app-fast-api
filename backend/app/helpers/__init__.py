"""
================================================================================
Farm Management System - Helper Modules
================================================================================

This package contains helper modules for cross-module integration and
utility functions.

Available Helpers:
-----------------
- inventory_integration: Helper for integrating modules with inventory system

Usage:
------
from app.helpers.inventory_integration import InventoryIntegration

inv = InventoryIntegration(module_name="biofloc")
result = await inv.deduct_stock(...)

================================================================================
"""

from app.helpers.inventory_integration import (
    InventoryIntegration,
    create_inventory_integration
)

__all__ = [
    "InventoryIntegration",
    "create_inventory_integration"
]
