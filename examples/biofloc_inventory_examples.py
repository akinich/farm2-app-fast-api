"""
================================================================================
Biofloc Inventory Integration - Usage Examples
================================================================================
Version: 1.0.0
Last Updated: 2025-11-18

Description:
-----------
Comprehensive examples showing how to integrate the biofloc module with the
inventory system using the InventoryIntegration helper.

These examples demonstrate:
1. Daily feeding operations with stock deduction
2. Water quality management with chemical usage
3. Stock level monitoring and alerts
4. Consumption reporting and analytics
5. Batch operations for multiple tanks

================================================================================
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from decimal import Decimal

# Import the inventory integration helper
from app.helpers.inventory_integration import InventoryIntegration


# ============================================================================
# EXAMPLE 1: DAILY FEEDING OPERATION
# ============================================================================

async def example_daily_feeding(tank_id: str, user_id: str):
    """
    Example: Deduct feed from inventory for daily feeding operation.

    This shows how to:
    - Initialize the integration helper
    - Deduct stock with tank reference
    - Handle the response with cost tracking
    """
    # Initialize integration for biofloc module
    inv = InventoryIntegration(module_name="biofloc")

    try:
        # Deduct 10.5 kg of feed
        result = await inv.deduct_stock(
            item_sku="FEED-PELLET-5MM",
            quantity=10.5,
            user_id=user_id,
            reference_id=tank_id,  # Links to specific tank
            notes="Daily morning feeding - Tank A"
        )

        # Process the result
        print(f"✓ Successfully deducted {result['quantity_deducted']} {result['unit']}")
        print(f"  Item: {result['item_name']} (SKU: {result['sku']})")
        print(f"  Cost: ${result['total_cost']:.2f}")
        print(f"  Average cost per unit: ${result['avg_cost']:.2f}")
        print(f"  Remaining stock: {result['new_balance']} {result['unit']}")

        # Log which batches were used (FIFO tracking)
        print("\n  Batches used:")
        for batch in result['batches_used']:
            print(f"    - Batch {batch['batch_number']}: "
                  f"{batch['qty_from_batch']} {result['unit']} "
                  f"@ ${batch['unit_cost']:.2f}/unit")

        return result

    except Exception as e:
        print(f"✗ Error during feeding operation: {str(e)}")
        # Handle error (e.g., insufficient stock, item not found)
        # Could trigger low stock alert or alternative action
        return None


# ============================================================================
# EXAMPLE 2: MULTIPLE ITEMS DEDUCTION (FEEDING SCHEDULE)
# ============================================================================

async def example_feeding_schedule(tank_id: str, user_id: str):
    """
    Example: Deduct multiple items for a complete feeding schedule.

    Use case: Tank requires both pellet feed and vitamin supplement.
    """
    inv = InventoryIntegration(module_name="biofloc")

    # Define feeding schedule
    feeding_items = [
        {"sku": "FEED-PELLET-5MM", "quantity": 10.5},
        {"sku": "FEED-VITAMIN-MIX", "quantity": 0.5},
        {"sku": "FEED-PROBIOTIC", "quantity": 0.2}
    ]

    result = await inv.deduct_multiple_items(
        items=feeding_items,
        user_id=user_id,
        reference_id=tank_id,
        notes=f"Complete feeding schedule - Tank {tank_id}"
    )

    print(f"\nFeeding Schedule Results:")
    print(f"  Total items: {result['total_items']}")
    print(f"  Successful: {result['successful']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Total cost: ${result['total_cost']:.2f}")

    # Check individual results
    for item_result in result['results']:
        if item_result['status'] == 'success':
            print(f"  ✓ {item_result['sku']}: Success")
        else:
            print(f"  ✗ {item_result['sku']}: {item_result['error']}")

    return result


# ============================================================================
# EXAMPLE 3: WATER QUALITY MANAGEMENT (CHEMICAL USAGE)
# ============================================================================

async def example_water_treatment(tank_id: str, user_id: str, treatment_type: str):
    """
    Example: Deduct chemicals for water quality management.

    Common treatments:
    - pH adjustment
    - Ammonia reduction
    - Algae control
    """
    inv = InventoryIntegration(module_name="biofloc")

    # Treatment protocols
    treatments = {
        "ph_adjustment": [
            {"sku": "CHEM-PH-DOWN", "quantity": 0.5}
        ],
        "ammonia_control": [
            {"sku": "CHEM-AMMONIA-REMOVER", "quantity": 1.0},
            {"sku": "CHEM-BENEFICIAL-BACTERIA", "quantity": 0.25}
        ],
        "algae_control": [
            {"sku": "CHEM-ALGAECIDE", "quantity": 0.75}
        ]
    }

    if treatment_type not in treatments:
        print(f"Unknown treatment type: {treatment_type}")
        return None

    result = await inv.deduct_multiple_items(
        items=treatments[treatment_type],
        user_id=user_id,
        reference_id=tank_id,
        notes=f"Water treatment: {treatment_type} - Tank {tank_id}"
    )

    print(f"\nWater Treatment Applied: {treatment_type}")
    print(f"  Items used: {result['successful']}/{result['total_items']}")
    print(f"  Treatment cost: ${result['total_cost']:.2f}")

    return result


# ============================================================================
# EXAMPLE 4: STOCK LEVEL MONITORING
# ============================================================================

async def example_check_stock_before_feeding():
    """
    Example: Check stock levels before starting daily feeding operations.

    Best practice: Verify stock availability before deducting to avoid
    mid-operation failures.
    """
    inv = InventoryIntegration(module_name="biofloc")

    # Items needed for today's operations
    required_items = {
        "FEED-PELLET-5MM": 50.0,      # Need 50kg for all tanks
        "FEED-VITAMIN-MIX": 2.0,       # Need 2kg
        "CHEM-PH-DOWN": 3.0            # Need 3 liters
    }

    print("\nStock Availability Check:")
    print("=" * 60)

    all_available = True

    for sku, required_qty in required_items.items():
        try:
            stock_info = await inv.check_stock_level(sku)

            is_available = stock_info['current_qty'] >= required_qty
            status = "✓" if is_available else "✗"

            print(f"{status} {stock_info['item_name']} ({sku}):")
            print(f"   Required: {required_qty} {stock_info['unit']}")
            print(f"   Available: {stock_info['current_qty']} {stock_info['unit']}")

            if stock_info['is_low_stock']:
                print(f"   ⚠ WARNING: Below reorder threshold!")
                print(f"   Deficit: {stock_info['deficit']} {stock_info['unit']}")

            if not is_available:
                all_available = False
                shortage = required_qty - stock_info['current_qty']
                print(f"   ⚠ INSUFFICIENT: Short by {shortage} {stock_info['unit']}")

            print()

        except Exception as e:
            print(f"✗ Error checking {sku}: {str(e)}\n")
            all_available = False

    print("=" * 60)
    if all_available:
        print("✓ All items available - Proceeding with operations")
    else:
        print("✗ Insufficient stock - Please restock before proceeding")

    return all_available


# ============================================================================
# EXAMPLE 5: LOW STOCK ALERTS FOR BIOFLOC OPERATIONS
# ============================================================================

async def example_monitor_low_stock():
    """
    Example: Monitor inventory for low stock alerts.

    Use case: Daily check to ensure adequate supplies for biofloc operations.
    Should be run as a scheduled task (e.g., cron job).
    """
    inv = InventoryIntegration(module_name="biofloc")

    print("\nLow Stock Alert Monitor")
    print("=" * 60)

    # Get all low stock items
    low_stock_items = await inv.get_low_stock_alerts()

    if not low_stock_items:
        print("✓ All items are adequately stocked")
        return []

    print(f"⚠ Found {len(low_stock_items)} items below reorder threshold:\n")

    # Categorize by priority
    critical = []  # Below minimum
    warning = []   # Below reorder threshold

    for item in low_stock_items:
        deficit = item['deficit']

        if item['current_qty'] < item.get('min_stock_level', 0):
            critical.append(item)
        else:
            warning.append(item)

    # Display critical items first
    if critical:
        print("🔴 CRITICAL (Below Minimum Stock Level):")
        for item in critical:
            print(f"   - {item['item_name']} ({item['sku']})")
            print(f"     Current: {item['current_qty']} {item['unit']}")
            print(f"     Needed: {item['reorder_threshold']} {item['unit']}")
            print(f"     Deficit: {item['deficit']} {item['unit']}")
            print(f"     Category: {item['category']}\n")

    # Display warning items
    if warning:
        print("🟡 WARNING (Below Reorder Threshold):")
        for item in warning:
            print(f"   - {item['item_name']} ({item['sku']})")
            print(f"     Current: {item['current_qty']} {item['unit']}")
            print(f"     Reorder at: {item['reorder_threshold']} {item['unit']}")
            print(f"     Category: {item['category']}\n")

    print("=" * 60)
    print(f"Action required: Create purchase orders for {len(low_stock_items)} items")

    return low_stock_items


# ============================================================================
# EXAMPLE 6: EXPIRING ITEMS ALERT
# ============================================================================

async def example_check_expiring_items(days: int = 30):
    """
    Example: Check for items expiring soon.

    Use case: Weekly check to identify items that need to be used before expiry.
    Helps reduce waste and plan feeding schedules.
    """
    inv = InventoryIntegration(module_name="biofloc")

    print(f"\nExpiring Items Check (Next {days} Days)")
    print("=" * 60)

    expiring_items = await inv.get_expiring_items(days=days)

    if not expiring_items:
        print(f"✓ No items expiring in the next {days} days")
        return []

    print(f"⚠ Found {len(expiring_items)} batches expiring soon:\n")

    for item in expiring_items:
        urgency = "🔴" if item['days_until_expiry'] <= 7 else "🟡"

        print(f"{urgency} {item['item_name']} ({item['sku']})")
        print(f"   Batch: {item['batch_number']}")
        print(f"   Quantity: {item['remaining_qty']} {item['unit']}")
        print(f"   Expires: {item['expiry_date']} ({item['days_until_expiry']} days)")
        print()

    print("=" * 60)
    print("Action: Prioritize using expiring items in feeding schedules")

    return expiring_items


# ============================================================================
# EXAMPLE 7: MONTHLY CONSUMPTION REPORT
# ============================================================================

async def example_monthly_consumption_report(
    month: int = None,
    year: int = None,
    tank_id: str = None
):
    """
    Example: Generate monthly consumption report for biofloc operations.

    Use case: Monthly analysis of feed and chemical usage, cost tracking,
    and budgeting for farm operations.
    """
    inv = InventoryIntegration(module_name="biofloc")

    # Default to current month if not specified
    if month is None or year is None:
        today = date.today()
        month = today.month
        year = today.year

    # Calculate date range
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    print(f"\n{'=' * 80}")
    print(f"BIOFLOC INVENTORY CONSUMPTION REPORT")
    print(f"Period: {start_date.strftime('%B %Y')}")
    if tank_id:
        print(f"Tank: {tank_id}")
    print(f"{'=' * 80}\n")

    # Get consumption report
    report = await inv.get_consumption_report(
        start_date=start_date,
        end_date=end_date,
        reference_id=tank_id
    )

    # Display summary
    print("SUMMARY:")
    print(f"  Total Items Used: {report['summary']['total_items']}")
    print(f"  Total Transactions: {report['summary']['total_transactions']}")
    print(f"  Total Cost: ${report['summary']['total_cost']:,.2f}")
    print()

    # Display by category
    feed_items = [i for i in report['items'] if 'FEED' in i['sku']]
    chem_items = [i for i in report['items'] if 'CHEM' in i['sku']]

    if feed_items:
        print("FEED CONSUMPTION:")
        feed_total = sum(i['total_cost'] for i in feed_items)
        for item in feed_items:
            print(f"  • {item['item_name']} ({item['sku']})")
            print(f"    Quantity: {item['quantity_consumed']:,.2f} {item['unit']}")
            print(f"    Avg Cost: ${item['avg_unit_cost']:.2f}/{item['unit']}")
            print(f"    Total Cost: ${item['total_cost']:,.2f}")
            print()
        print(f"  Feed Subtotal: ${feed_total:,.2f}\n")

    if chem_items:
        print("CHEMICAL USAGE:")
        chem_total = sum(i['total_cost'] for i in chem_items)
        for item in chem_items:
            print(f"  • {item['item_name']} ({item['sku']})")
            print(f"    Quantity: {item['quantity_consumed']:,.2f} {item['unit']}")
            print(f"    Avg Cost: ${item['avg_unit_cost']:.2f}/{item['unit']}")
            print(f"    Total Cost: ${item['total_cost']:,.2f}")
            print()
        print(f"  Chemical Subtotal: ${chem_total:,.2f}\n")

    # Cost breakdown
    if feed_items and chem_items:
        print("COST BREAKDOWN:")
        total = report['summary']['total_cost']
        feed_pct = (feed_total / total * 100) if total > 0 else 0
        chem_pct = (chem_total / total * 100) if total > 0 else 0
        print(f"  Feed: ${feed_total:,.2f} ({feed_pct:.1f}%)")
        print(f"  Chemicals: ${chem_total:,.2f} ({chem_pct:.1f}%)")
        print()

    print(f"{'=' * 80}")

    return report


# ============================================================================
# EXAMPLE 8: DETAILED TRANSACTION HISTORY FOR A TANK
# ============================================================================

async def example_tank_transaction_history(
    tank_id: str,
    days: int = 30
):
    """
    Example: Get detailed transaction history for a specific tank.

    Use case: Audit trail, troubleshooting, or analyzing tank-specific costs.
    """
    inv = InventoryIntegration(module_name="biofloc")

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    print(f"\nTransaction History - Tank {tank_id}")
    print(f"Period: {start_date} to {end_date}")
    print("=" * 80)

    transactions = await inv.get_detailed_transactions(
        start_date=start_date,
        end_date=end_date,
        reference_id=tank_id,
        limit=50
    )

    if not transactions:
        print("No transactions found for this period.")
        return []

    total_cost = 0.0

    for idx, txn in enumerate(transactions, 1):
        print(f"\n{idx}. {txn['transaction_date']} - {txn['item_name']}")
        print(f"   SKU: {txn['sku']}")
        print(f"   Quantity: {txn['quantity']} {txn['unit']}")
        print(f"   Batch: {txn['batch_number']}")
        print(f"   Cost: ${txn['total_cost']:.2f} (@ ${txn['unit_cost']:.2f}/{txn['unit']})")
        print(f"   New Balance: {txn['new_balance']} {txn['unit']}")
        print(f"   User: {txn['user_name']}")
        if txn['notes']:
            print(f"   Notes: {txn['notes']}")

        total_cost += txn['total_cost']

    print(f"\n{'=' * 80}")
    print(f"Total Transactions: {len(transactions)}")
    print(f"Total Cost: ${total_cost:.2f}")

    return transactions


# ============================================================================
# EXAMPLE 9: GET ALL FEED ITEMS (BY CATEGORY)
# ============================================================================

async def example_get_feed_items():
    """
    Example: Get all feed items from inventory.

    Use case: Populate dropdown menus, create feeding schedules,
    or inventory management dashboards.
    """
    inv = InventoryIntegration(module_name="biofloc")

    print("\nAvailable Feed Items:")
    print("=" * 60)

    feed_items = await inv.get_items_by_category("Feed")

    if not feed_items:
        print("No feed items found.")
        return []

    for item in feed_items:
        status = "✓" if not item.get('is_low_stock', False) else "⚠"

        print(f"{status} {item['item_name']} ({item['sku']})")
        print(f"   Stock: {item['current_qty']} {item['unit']}")
        print(f"   Reorder at: {item['reorder_threshold']} {item['unit']}")
        print()

    return feed_items


# ============================================================================
# EXAMPLE 10: COMPLETE DAILY OPERATIONS WORKFLOW
# ============================================================================

async def example_daily_operations_workflow(user_id: str):
    """
    Example: Complete daily workflow combining multiple operations.

    This demonstrates a typical daily routine:
    1. Check stock levels
    2. Check for low stock/expiring items
    3. Perform feeding operations
    4. Log results
    """
    print("\n" + "=" * 80)
    print("BIOFLOC DAILY OPERATIONS - INVENTORY WORKFLOW")
    print("=" * 80)

    inv = InventoryIntegration(module_name="biofloc")

    # Step 1: Morning stock check
    print("\n[STEP 1] Morning Stock Check")
    print("-" * 80)
    stock_ok = await example_check_stock_before_feeding()

    if not stock_ok:
        print("\n⚠ Aborting operations due to insufficient stock")
        return

    # Step 2: Check for alerts
    print("\n[STEP 2] Alert Monitoring")
    print("-" * 80)
    low_stock = await inv.get_low_stock_alerts()
    expiring = await inv.get_expiring_items(days=7)

    if low_stock:
        print(f"⚠ {len(low_stock)} items need reordering")
    if expiring:
        print(f"⚠ {len(expiring)} items expiring within 7 days")

    # Step 3: Execute feeding operations for multiple tanks
    print("\n[STEP 3] Feeding Operations")
    print("-" * 80)

    tanks = [
        {"id": "tank-001", "name": "Tank A"},
        {"id": "tank-002", "name": "Tank B"},
        {"id": "tank-003", "name": "Tank C"}
    ]

    total_cost = 0.0

    for tank in tanks:
        print(f"\nFeeding {tank['name']}...")

        result = await inv.deduct_stock(
            item_sku="FEED-PELLET-5MM",
            quantity=10.5,
            user_id=user_id,
            reference_id=tank['id'],
            notes=f"Daily feeding - {tank['name']}"
        )

        if result:
            print(f"✓ Complete - Cost: ${result['total_cost']:.2f}")
            total_cost += result['total_cost']
        else:
            print(f"✗ Failed")

    # Step 4: Summary
    print("\n" + "=" * 80)
    print("DAILY OPERATIONS SUMMARY")
    print("=" * 80)
    print(f"Tanks Fed: {len(tanks)}")
    print(f"Total Feeding Cost: ${total_cost:.2f}")
    print(f"Low Stock Alerts: {len(low_stock)}")
    print(f"Expiring Items: {len(expiring)}")
    print("=" * 80)


# ============================================================================
# EXAMPLE 11: ERROR HANDLING PATTERNS
# ============================================================================

async def example_error_handling(tank_id: str, user_id: str):
    """
    Example: Proper error handling for inventory operations.

    Shows how to handle common errors:
    - Item not found
    - Insufficient stock
    - Database errors
    """
    inv = InventoryIntegration(module_name="biofloc")

    # Pattern 1: Try-catch with specific error handling
    try:
        result = await inv.deduct_stock(
            item_sku="FEED-PELLET-5MM",
            quantity=1000.0,  # Intentionally large quantity
            user_id=user_id,
            reference_id=tank_id,
            notes="Test deduction"
        )
        print("✓ Deduction successful")
        return result

    except HTTPException as e:
        if e.status_code == 404:
            print(f"✗ Item not found: {e.detail}")
            # Could trigger: Create item, notify admin, use alternative

        elif e.status_code == 400 and "Insufficient stock" in str(e.detail):
            print(f"✗ Insufficient stock")
            if isinstance(e.detail, dict):
                print(f"   Requested: {e.detail.get('requested')}")
                print(f"   Available: {e.detail.get('available')}")
                print(f"   Deficit: {e.detail.get('deficit')}")
            # Could trigger: Low stock alert, emergency reorder, pause operations

        else:
            print(f"✗ Error: {e.detail}")

        return None

    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        # Log error, notify admin, rollback operations
        return None

    # Pattern 2: Pre-check before operation
    is_available = await inv.is_stock_available(
        item_sku="FEED-PELLET-5MM",
        required_quantity=1000.0
    )

    if not is_available:
        print("⚠ Stock check failed - Skipping operation")
        return None

    # Proceed with operation knowing stock is available
    result = await inv.deduct_stock(
        item_sku="FEED-PELLET-5MM",
        quantity=1000.0,
        user_id=user_id,
        reference_id=tank_id
    )
    return result


# ============================================================================
# MAIN DEMO FUNCTION
# ============================================================================

async def run_all_examples():
    """Run all examples to demonstrate inventory integration capabilities."""

    # Mock user and tank IDs (replace with real IDs in production)
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    tank_id = "tank-001"

    print("\n" + "=" * 80)
    print("BIOFLOC INVENTORY INTEGRATION - COMPREHENSIVE EXAMPLES")
    print("=" * 80)

    # Run examples
    await example_daily_feeding(tank_id, user_id)
    await example_feeding_schedule(tank_id, user_id)
    await example_water_treatment(tank_id, user_id, "ammonia_control")
    await example_check_stock_before_feeding()
    await example_monitor_low_stock()
    await example_check_expiring_items(30)
    await example_monthly_consumption_report()
    await example_tank_transaction_history(tank_id, 30)
    await example_get_feed_items()
    await example_daily_operations_workflow(user_id)
    await example_error_handling(tank_id, user_id)

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)


# ============================================================================
# QUICK REFERENCE
# ============================================================================

"""
QUICK REFERENCE - Common Operations:

1. Initialize Integration:
   inv = InventoryIntegration(module_name="biofloc")

2. Deduct Single Item:
   result = await inv.deduct_stock(
       item_sku="FEED-001",
       quantity=10.5,
       user_id=user_id,
       reference_id=tank_id,
       notes="Daily feeding"
   )

3. Deduct Multiple Items:
   result = await inv.deduct_multiple_items(
       items=[{"sku": "FEED-001", "quantity": 10}],
       user_id=user_id,
       reference_id=tank_id
   )

4. Check Stock Level:
   stock = await inv.check_stock_level("FEED-001")

5. Get Low Stock Alerts:
   alerts = await inv.get_low_stock_alerts()

6. Get Expiring Items:
   expiring = await inv.get_expiring_items(days=30)

7. Generate Report:
   report = await inv.get_consumption_report(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 1, 31)
   )

8. Get Item Details:
   item = await inv.get_item_by_sku("FEED-001")

9. Get Items by Category:
   feed_items = await inv.get_items_by_category("Feed")
"""
