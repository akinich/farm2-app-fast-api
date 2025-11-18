# Biofloc Inventory Integration Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-18

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup & Configuration](#setup--configuration)
4. [Core Concepts](#core-concepts)
5. [Integration Helper API](#integration-helper-api)
6. [Common Use Cases](#common-use-cases)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide explains how to integrate the **Biofloc** module with the **Inventory** module using the `InventoryIntegration` helper class. The integration enables:

- ✅ **Stock deduction** for feeding operations with FIFO cost tracking
- ✅ **Stock level monitoring** and alerts
- ✅ **Consumption tracking** by tank/batch
- ✅ **Cost analysis** and reporting
- ✅ **Automatic audit trails** for all operations

### Why Use the Integration Helper?

Instead of calling inventory endpoints directly, the `InventoryIntegration` helper provides:

1. **Simplified API** - Cleaner, more intuitive method calls
2. **Automatic module tracking** - All operations tagged as "biofloc"
3. **Error handling** - Built-in exception handling and logging
4. **Type conversion** - Handles Decimal/float conversions automatically
5. **Batch operations** - Deduct multiple items easily
6. **Reporting utilities** - Pre-built consumption reports

---

## Architecture

### System Components

```
┌─────────────────┐
│  Biofloc Module │
│  (Your Code)    │
└────────┬────────┘
         │
         │ Uses
         ▼
┌─────────────────────────────┐
│ InventoryIntegration Helper │  ← You interact with this
│ (Simplified Interface)       │
└────────┬────────────────────┘
         │
         │ Calls
         ▼
┌─────────────────────────┐
│ Inventory Service       │
│ (Business Logic)        │
└────────┬────────────────┘
         │
         │ Executes
         ▼
┌─────────────────────────┐
│ Database (PostgreSQL)   │
│ - item_master           │
│ - inventory_batches     │
│ - inventory_transactions│
└─────────────────────────┘
```

### Data Flow Example: Daily Feeding

```
1. Biofloc calls:
   inv.deduct_stock(sku="FEED-001", quantity=10.5, tank_id="tank-001")

2. Integration helper:
   - Looks up item by SKU
   - Validates stock availability
   - Calls inventory_service.use_stock_fifo()
   - Tags transaction with module_reference="biofloc"
   - Returns formatted result

3. Inventory service:
   - Retrieves batches (FIFO order)
   - Deducts from oldest batches first
   - Updates inventory_batches.remaining_qty
   - Creates inventory_transactions records
   - Triggers auto-update of item_master.current_qty

4. Database:
   - Commits transaction atomically
   - Returns new balances and costs
```

---

## Setup & Configuration

### 1. File Location

The integration helper is located at:
```
backend/app/helpers/inventory_integration.py
```

### 2. Import in Your Module

```python
from app.helpers.inventory_integration import InventoryIntegration

# Initialize for biofloc module
inv = InventoryIntegration(module_name="biofloc")
```

### 3. Dependencies

The helper requires:
- `app.database` - Database connection utilities
- `app.services.inventory_service` - Core inventory logic
- Python 3.8+ (for type hints)
- `asyncpg` (async PostgreSQL driver)

### 4. Authentication

All inventory operations require authentication. Ensure you have:
- Valid JWT token for API calls
- User with "inventory" module permission
- User ID available for audit trail

---

## Core Concepts

### 1. Module Reference

Every inventory transaction is tagged with `module_reference="biofloc"`. This allows:
- Filtering biofloc-specific transactions
- Generating module-specific reports
- Auditing cross-module usage

### 2. Reference ID (tank_id)

The `reference_id` parameter (stored as `tank_id` in database) links inventory operations to specific tanks:

```python
await inv.deduct_stock(
    item_sku="FEED-001",
    quantity=10.5,
    reference_id="tank-abc-123",  # Links to specific tank
    notes="Daily feeding"
)
```

This enables:
- Tank-specific consumption reports
- Cost allocation per tank
- Audit trail by tank

### 3. SKU-based Identification

Items are identified by **SKU (Stock Keeping Unit)** rather than database IDs:

```python
# Good - Using SKU (human-readable)
await inv.deduct_stock(item_sku="FEED-PELLET-5MM", quantity=10)

# Avoid - Using database UUID
# await inv.deduct_stock(item_id="550e8400-e29b-...", quantity=10)
```

**Benefits:**
- More readable code
- Consistent across environments
- Easier to configure feeding schedules

### 4. FIFO (First-In-First-Out) Logic

Stock deduction automatically uses FIFO:
- Oldest batches are used first
- Each batch tracks its purchase date
- Cost is calculated as weighted average across batches used

**Example:**

```
Available batches:
  Batch A: 10kg @ $5/kg (purchased Jan 1)
  Batch B: 20kg @ $6/kg (purchased Jan 15)

Deduct 15kg:
  - Use 10kg from Batch A (@ $5/kg) = $50
  - Use 5kg from Batch B (@ $6/kg) = $30
  - Total: 15kg @ $5.33/kg average = $80
```

### 5. Audit Trail

Every operation is automatically logged in `inventory_transactions` table:

```sql
transaction_type: 'use'
module_reference: 'biofloc'
tank_id: 'tank-001'
quantity_change: -10.5
user_id: [authenticated user]
transaction_date: [timestamp]
notes: 'Daily feeding'
```

---

## Integration Helper API

### Initialization

```python
inv = InventoryIntegration(module_name="biofloc")
```

### Stock Deduction Methods

#### `deduct_stock()` - Single Item

Deduct a single item from inventory.

```python
result = await inv.deduct_stock(
    item_sku: str,              # SKU of item (e.g., "FEED-001")
    quantity: float,            # Amount to deduct
    user_id: str,               # UUID of user
    reference_id: str = None,   # Optional tank/batch reference
    notes: str = None           # Optional notes
)
```

**Returns:**
```python
{
    "success": True,
    "item_name": "Pellet Feed 5mm",
    "sku": "FEED-PELLET-5MM",
    "quantity_deducted": 10.5,
    "unit": "kg",
    "batches_used": [
        {
            "batch_id": "uuid",
            "batch_number": "B001",
            "qty_from_batch": 10.5,
            "unit_cost": 5.00,
            "cost": 52.50
        }
    ],
    "total_cost": 52.50,
    "avg_cost": 5.00,
    "new_balance": 89.5
}
```

**Raises:**
- `HTTPException(404)` - Item not found
- `HTTPException(400)` - Insufficient stock

---

#### `deduct_multiple_items()` - Batch Operation

Deduct multiple items (e.g., for a feeding schedule).

```python
result = await inv.deduct_multiple_items(
    items: List[Dict],          # [{"sku": "FEED-001", "quantity": 10.5}, ...]
    user_id: str,
    reference_id: str = None,
    notes: str = None
)
```

**Returns:**
```python
{
    "total_items": 3,
    "successful": 2,
    "failed": 1,
    "results": [
        {"sku": "FEED-001", "status": "success", "result": {...}},
        {"sku": "FEED-002", "status": "success", "result": {...}},
        {"sku": "FEED-003", "status": "failed", "error": "Insufficient stock"}
    ],
    "total_cost": 125.50
}
```

**Note:** Operations are NOT atomic - each item is processed separately.

---

### Stock Level Checking Methods

#### `check_stock_level()` - Single Item

Check current stock for an item.

```python
stock = await inv.check_stock_level(item_sku: str)
```

**Returns:**
```python
{
    "sku": "FEED-001",
    "item_name": "Pellet Feed",
    "current_qty": 100.5,
    "unit": "kg",
    "reorder_threshold": 50.0,
    "min_stock_level": 20.0,
    "is_low_stock": False,
    "deficit": 0.0
}
```

---

#### `check_multiple_stock_levels()` - Multiple Items

Check stock for multiple items at once.

```python
stocks = await inv.check_multiple_stock_levels(
    item_skus: List[str]
)
```

---

#### `is_stock_available()` - Availability Check

Quick boolean check if sufficient stock exists.

```python
available = await inv.is_stock_available(
    item_sku: str,
    required_quantity: float
)
# Returns: True or False
```

---

### Alert Methods

#### `get_low_stock_alerts()` - Low Stock Items

Get all items below reorder threshold.

```python
alerts = await inv.get_low_stock_alerts()
```

**Returns:**
```python
[
    {
        "sku": "FEED-001",
        "item_name": "Pellet Feed",
        "current_qty": 15.0,
        "reorder_threshold": 50.0,
        "deficit": 35.0,
        "unit": "kg",
        "category": "Feed"
    },
    ...
]
```

---

#### `get_expiring_items()` - Expiry Alerts

Get items expiring within specified days.

```python
expiring = await inv.get_expiring_items(days: int = 30)
```

**Returns:**
```python
[
    {
        "sku": "FEED-001",
        "item_name": "Pellet Feed",
        "batch_number": "B123",
        "remaining_qty": 50.0,
        "unit": "kg",
        "expiry_date": "2025-02-15",
        "days_until_expiry": 7
    },
    ...
]
```

---

### Reporting Methods

#### `get_consumption_report()` - Period Summary

Generate consumption report for a date range.

```python
report = await inv.get_consumption_report(
    start_date: date,
    end_date: date,
    item_sku: str = None,        # Optional: filter by item
    reference_id: str = None     # Optional: filter by tank
)
```

**Returns:**
```python
{
    "module": "biofloc",
    "period": {
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    },
    "summary": {
        "total_items": 5,
        "total_transactions": 93,
        "total_cost": 1250.75
    },
    "items": [
        {
            "sku": "FEED-001",
            "item_name": "Pellet Feed",
            "unit": "kg",
            "quantity_consumed": 315.0,
            "transaction_count": 31,
            "total_cost": 1575.00,
            "avg_unit_cost": 5.00
        },
        ...
    ]
}
```

---

#### `get_detailed_transactions()` - Transaction History

Get detailed transaction log.

```python
transactions = await inv.get_detailed_transactions(
    start_date: date = None,
    end_date: date = None,
    item_sku: str = None,
    reference_id: str = None,
    limit: int = 100
)
```

**Returns:** List of transaction details with timestamps, quantities, costs, users, etc.

---

### Item Lookup Methods

#### `get_item_by_sku()` - Item Details

Get full item details by SKU.

```python
item = await inv.get_item_by_sku(sku: str)
```

---

#### `get_items_by_category()` - Category Listing

Get all items in a category.

```python
feed_items = await inv.get_items_by_category(category: str)
```

---

## Common Use Cases

### Use Case 1: Daily Feeding Operation

```python
from app.helpers.inventory_integration import InventoryIntegration

async def daily_feeding(tank_id: str, user_id: str):
    inv = InventoryIntegration(module_name="biofloc")

    result = await inv.deduct_stock(
        item_sku="FEED-PELLET-5MM",
        quantity=10.5,
        user_id=user_id,
        reference_id=tank_id,
        notes="Daily morning feeding"
    )

    print(f"Fed {result['quantity_deducted']} {result['unit']}")
    print(f"Cost: ${result['total_cost']:.2f}")
    print(f"Remaining: {result['new_balance']} {result['unit']}")
```

---

### Use Case 2: Multi-Item Feeding Schedule

```python
async def feeding_schedule(tank_id: str, user_id: str):
    inv = InventoryIntegration(module_name="biofloc")

    # Define schedule
    schedule = [
        {"sku": "FEED-PELLET-5MM", "quantity": 10.5},
        {"sku": "FEED-VITAMIN-MIX", "quantity": 0.5},
        {"sku": "FEED-PROBIOTIC", "quantity": 0.2}
    ]

    result = await inv.deduct_multiple_items(
        items=schedule,
        user_id=user_id,
        reference_id=tank_id,
        notes="Complete feeding schedule"
    )

    print(f"Successful: {result['successful']}/{result['total_items']}")
    print(f"Total cost: ${result['total_cost']:.2f}")
```

---

### Use Case 3: Pre-Check Before Operation

```python
async def safe_feeding(tank_id: str, user_id: str):
    inv = InventoryIntegration(module_name="biofloc")

    # Check availability first
    available = await inv.is_stock_available(
        item_sku="FEED-PELLET-5MM",
        required_quantity=10.5
    )

    if not available:
        print("⚠ Insufficient stock - Aborting operation")
        # Trigger alert, reorder, etc.
        return None

    # Proceed with deduction
    result = await inv.deduct_stock(
        item_sku="FEED-PELLET-5MM",
        quantity=10.5,
        user_id=user_id,
        reference_id=tank_id
    )

    return result
```

---

### Use Case 4: Morning Stock Check

```python
async def morning_stock_check():
    inv = InventoryIntegration(module_name="biofloc")

    # Check for low stock
    low_stock = await inv.get_low_stock_alerts()

    if low_stock:
        print(f"⚠ {len(low_stock)} items need reordering:")
        for item in low_stock:
            print(f"  - {item['item_name']}: "
                  f"{item['current_qty']} {item['unit']} "
                  f"(need {item['deficit']} more)")

    # Check for expiring items
    expiring = await inv.get_expiring_items(days=7)

    if expiring:
        print(f"⚠ {len(expiring)} items expiring within 7 days:")
        for item in expiring:
            print(f"  - {item['item_name']} Batch {item['batch_number']}: "
                  f"{item['remaining_qty']} {item['unit']} "
                  f"(expires in {item['days_until_expiry']} days)")
```

---

### Use Case 5: Monthly Cost Report

```python
from datetime import date

async def monthly_cost_report(month: int, year: int):
    inv = InventoryIntegration(module_name="biofloc")

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    report = await inv.get_consumption_report(
        start_date=start_date,
        end_date=end_date
    )

    print(f"Month: {start_date.strftime('%B %Y')}")
    print(f"Total Cost: ${report['summary']['total_cost']:,.2f}")
    print(f"Transactions: {report['summary']['total_transactions']}")

    for item in report['items']:
        print(f"\n{item['item_name']} ({item['sku']}):")
        print(f"  Consumed: {item['quantity_consumed']} {item['unit']}")
        print(f"  Cost: ${item['total_cost']:,.2f}")
```

---

### Use Case 6: Tank-Specific Analysis

```python
async def tank_cost_analysis(tank_id: str, days: int = 30):
    from datetime import timedelta

    inv = InventoryIntegration(module_name="biofloc")

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    report = await inv.get_consumption_report(
        start_date=start_date,
        end_date=end_date,
        reference_id=tank_id  # Filter by specific tank
    )

    print(f"Tank {tank_id} - Last {days} days:")
    print(f"Total cost: ${report['summary']['total_cost']:,.2f}")
    print(f"Daily average: ${report['summary']['total_cost'] / days:.2f}")
```

---

## Error Handling

### Common Errors

#### 1. Item Not Found (404)

```python
try:
    result = await inv.deduct_stock(
        item_sku="INVALID-SKU",
        quantity=10,
        user_id=user_id
    )
except HTTPException as e:
    if e.status_code == 404:
        print(f"Item not found: {e.detail}")
        # Handle: Create item, use alternative, notify admin
```

#### 2. Insufficient Stock (400)

```python
try:
    result = await inv.deduct_stock(
        item_sku="FEED-001",
        quantity=1000,  # More than available
        user_id=user_id
    )
except HTTPException as e:
    if e.status_code == 400 and "Insufficient stock" in str(e.detail):
        # Error detail contains: requested, available, deficit
        print(f"Not enough stock!")
        print(f"  Requested: {e.detail['requested']}")
        print(f"  Available: {e.detail['available']}")
        print(f"  Deficit: {e.detail['deficit']}")

        # Handle: Alert user, emergency reorder, pause operations
```

#### 3. Database Errors (500)

```python
try:
    result = await inv.deduct_stock(...)
except HTTPException as e:
    if e.status_code == 500:
        print(f"Database error: {e.detail}")
        # Log error, retry, notify admin
```

### Error Handling Best Practices

1. **Always wrap operations in try-except blocks**
2. **Pre-check stock availability for critical operations**
3. **Log all errors for debugging**
4. **Provide fallback mechanisms (alternative items, pause operations)**
5. **Monitor error rates and set up alerts**

---

## Best Practices

### 1. Use Pre-Checks for Critical Operations

```python
# Good - Check before deducting
if await inv.is_stock_available("FEED-001", required_qty):
    await inv.deduct_stock(...)
else:
    # Handle shortage before attempting deduction
```

### 2. Add Meaningful Notes

```python
# Good - Descriptive notes
notes = f"Daily feeding - Tank A - Batch {batch_number} - {datetime.now()}"

# Avoid - Generic notes
notes = "feeding"
```

### 3. Always Pass reference_id for Tracking

```python
# Good - Links to specific tank
await inv.deduct_stock(..., reference_id=tank_id)

# Avoid - No reference
await inv.deduct_stock(..., reference_id=None)
```

### 4. Monitor Alerts Daily

```python
# Run as scheduled task (cron job)
async def daily_monitoring():
    inv = InventoryIntegration(module_name="biofloc")

    low_stock = await inv.get_low_stock_alerts()
    expiring = await inv.get_expiring_items(days=7)

    # Send notifications, create POs, etc.
```

### 5. Generate Regular Reports

```python
# Monthly cost reports
async def end_of_month_report():
    report = await inv.get_consumption_report(
        start_date=first_day_of_month,
        end_date=last_day_of_month
    )
    # Store in database, send to management, etc.
```

### 6. Cache Item Lookups

```python
# Cache frequently used items
class FeedingService:
    def __init__(self):
        self.inv = InventoryIntegration(module_name="biofloc")
        self.item_cache = {}

    async def get_item(self, sku: str):
        if sku not in self.item_cache:
            self.item_cache[sku] = await self.inv.get_item_by_sku(sku)
        return self.item_cache[sku]
```

---

## Performance Considerations

### 1. Database Queries

- Each `deduct_stock()` call makes ~3-5 database queries
- Use `deduct_multiple_items()` instead of loops when possible
- Pre-fetch item details if needed multiple times

### 2. Batch Operations

```python
# Slow - Multiple individual calls
for item in items:
    await inv.deduct_stock(item['sku'], item['qty'], user_id)

# Faster - Single batch operation
await inv.deduct_multiple_items(items, user_id)
```

### 3. Report Generation

- Reports can be slow for large date ranges
- Consider generating reports asynchronously
- Cache frequently accessed reports

### 4. Connection Pooling

The integration uses the application's database pool:
- Min connections: 10
- Max connections: 50
- Automatic connection recycling

---

## Troubleshooting

### Issue: "Item not found" error

**Cause:** SKU doesn't exist in database

**Solution:**
1. Check SKU spelling
2. Verify item exists: `SELECT * FROM item_master WHERE sku = 'YOUR-SKU'`
3. Create item if needed via inventory admin endpoints

---

### Issue: "Insufficient stock" despite UI showing stock

**Cause:** Stock is in inactive batches or expired

**Solution:**
1. Check batch status: `SELECT * FROM inventory_batches WHERE item_master_id = '...' AND is_active = true`
2. Verify expiry dates
3. Create manual stock adjustment if needed

---

### Issue: Transactions not appearing in reports

**Cause:** Wrong date range or module_reference filter

**Solution:**
1. Verify date range includes transaction date
2. Check `module_reference` is "biofloc"
3. Query directly: `SELECT * FROM inventory_transactions WHERE module_reference = 'biofloc'`

---

### Issue: Slow performance

**Cause:** Large transaction history or missing indexes

**Solution:**
1. Check database indexes are present
2. Limit date ranges for reports
3. Use pagination for large result sets

---

## Additional Resources

- **API Documentation**: `/backend/README.md`
- **Database Schema**: `/sql_scripts/v1.0.0_initial_schema.sql`
- **Example Code**: `/examples/biofloc_inventory_examples.py`
- **Inventory Service**: `/backend/app/services/inventory_service.py`

---

## Support & Feedback

For issues, questions, or feature requests, please contact the development team or create an issue in the project repository.

---

**End of Integration Guide**
