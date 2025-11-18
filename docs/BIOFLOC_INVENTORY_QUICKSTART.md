# Biofloc ↔ Inventory Integration Quick Start

**5-Minute Guide** to integrating biofloc operations with inventory management.

---

## 📋 TL;DR - Copy & Paste Template

```python
from app.helpers.inventory_integration import InventoryIntegration

# 1. Initialize
inv = InventoryIntegration(module_name="biofloc")

# 2. Deduct stock for feeding
result = await inv.deduct_stock(
    item_sku="FEED-PELLET-5MM",
    quantity=10.5,
    user_id=current_user.id,
    reference_id=tank.id,
    notes="Daily feeding"
)

# 3. Check the result
print(f"✓ Deducted {result['quantity_deducted']} {result['unit']}")
print(f"  Cost: ${result['total_cost']:.2f}")
print(f"  Remaining: {result['new_balance']} {result['unit']}")
```

---

## 🎯 Top 5 Operations You'll Need

### 1️⃣ Deduct Stock (Daily Feeding)

```python
inv = InventoryIntegration(module_name="biofloc")

result = await inv.deduct_stock(
    item_sku="FEED-PELLET-5MM",  # Use SKU, not database ID
    quantity=10.5,                # Amount to deduct
    user_id=user_id,              # For audit trail
    reference_id=tank_id,         # Links to your tank
    notes="Daily feeding Tank A"  # Optional but recommended
)
```

**What you get back:**
- ✅ Cost breakdown (FIFO calculated)
- ✅ Batches used (which batches were deducted from)
- ✅ New balance (remaining stock)
- ✅ Automatic audit log created

---

### 2️⃣ Check Stock Before Operation

```python
# Simple boolean check
available = await inv.is_stock_available(
    item_sku="FEED-PELLET-5MM",
    required_quantity=50.0
)

if available:
    # Proceed with feeding
    await inv.deduct_stock(...)
else:
    # Alert user, trigger reorder, etc.
    print("⚠ Insufficient stock!")
```

---

### 3️⃣ Get Low Stock Alerts

```python
# Run this daily (cron job)
alerts = await inv.get_low_stock_alerts()

for item in alerts:
    print(f"⚠ {item['item_name']}: {item['current_qty']} {item['unit']}")
    print(f"   Need to order: {item['deficit']} {item['unit']}")
```

---

### 4️⃣ Monthly Cost Report

```python
from datetime import date

report = await inv.get_consumption_report(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31)
)

print(f"Total cost: ${report['summary']['total_cost']:,.2f}")
print(f"Transactions: {report['summary']['total_transactions']}")

# Breakdown by item
for item in report['items']:
    print(f"{item['item_name']}: ${item['total_cost']:.2f}")
```

---

### 5️⃣ Deduct Multiple Items (Feeding Schedule)

```python
schedule = [
    {"sku": "FEED-PELLET-5MM", "quantity": 10.5},
    {"sku": "FEED-VITAMIN-MIX", "quantity": 0.5},
    {"sku": "FEED-PROBIOTIC", "quantity": 0.2}
]

result = await inv.deduct_multiple_items(
    items=schedule,
    user_id=user_id,
    reference_id=tank_id
)

print(f"Successful: {result['successful']}/{result['total_items']}")
print(f"Total cost: ${result['total_cost']:.2f}")
```

---

## 🚨 Error Handling Essentials

```python
from fastapi import HTTPException

try:
    result = await inv.deduct_stock(...)

except HTTPException as e:
    if e.status_code == 404:
        print("❌ Item not found - Check SKU")

    elif e.status_code == 400 and "Insufficient stock" in str(e.detail):
        print("❌ Not enough stock!")
        print(f"   Available: {e.detail['available']}")
        print(f"   Needed: {e.detail['requested']}")
        # Trigger alert, emergency reorder, pause operations

    else:
        print(f"❌ Error: {e.detail}")
```

---

## 📊 Available Inventory Items

Common SKUs you'll use:

### Feed Items
- `FEED-PELLET-5MM` - Standard pellet feed (5mm)
- `FEED-PELLET-3MM` - Small pellet feed (3mm)
- `FEED-VITAMIN-MIX` - Vitamin supplement
- `FEED-PROBIOTIC` - Probiotic supplement

### Chemicals
- `CHEM-PH-DOWN` - pH reducer
- `CHEM-PH-UP` - pH increaser
- `CHEM-AMMONIA-REMOVER` - Ammonia treatment
- `CHEM-BENEFICIAL-BACTERIA` - Biofloc bacteria
- `CHEM-ALGAECIDE` - Algae control

> **Note:** Check your database for actual SKUs:
> ```sql
> SELECT sku, item_name, category FROM item_master WHERE is_active = true;
> ```

---

## 🔄 Complete Daily Workflow Example

```python
async def daily_biofloc_operations(user_id: str):
    inv = InventoryIntegration(module_name="biofloc")

    # 1. Morning: Check alerts
    low_stock = await inv.get_low_stock_alerts()
    if low_stock:
        # Send notifications to admin
        notify_low_stock(low_stock)

    # 2. Check expiring items
    expiring = await inv.get_expiring_items(days=7)
    if expiring:
        # Prioritize using expiring items
        prioritize_batches(expiring)

    # 3. Perform feeding for all tanks
    tanks = get_active_tanks()  # Your function

    for tank in tanks:
        try:
            # Check stock first
            if not await inv.is_stock_available("FEED-PELLET-5MM", tank.daily_feed_amount):
                alert_insufficient_stock(tank)
                continue

            # Deduct stock
            result = await inv.deduct_stock(
                item_sku="FEED-PELLET-5MM",
                quantity=tank.daily_feed_amount,
                user_id=user_id,
                reference_id=tank.id,
                notes=f"Daily feeding - {tank.name}"
            )

            # Log success
            log_feeding_success(tank, result)

        except Exception as e:
            log_feeding_error(tank, e)
            continue
```

---

## 💡 Best Practices

### ✅ DO:
- Always use `reference_id` to link to tanks
- Add descriptive `notes` for audit trail
- Check stock availability before critical operations
- Monitor low stock alerts daily
- Generate monthly cost reports

### ❌ DON'T:
- Use database UUIDs - use SKUs instead
- Forget error handling
- Skip `reference_id` (makes reporting useless)
- Ignore low stock alerts
- Perform large batch operations without pre-checks

---

## 🎓 Where to Learn More

1. **Full Examples**: `/examples/biofloc_inventory_examples.py`
   - 11 complete examples with detailed explanations

2. **Integration Guide**: `/docs/INVENTORY_INTEGRATION_GUIDE.md`
   - Complete API reference
   - Architecture details
   - Troubleshooting guide

3. **Helper Code**: `/backend/app/helpers/inventory_integration.py`
   - Source code with inline documentation

4. **Inventory API**: `/backend/app/routes/inventory.py`
   - Direct API endpoints (if you need them)

---

## 🔧 Setup Instructions

### 1. Import the Helper

```python
from app.helpers.inventory_integration import InventoryIntegration
```

### 2. Initialize for Biofloc

```python
inv = InventoryIntegration(module_name="biofloc")
```

### 3. Ensure Authentication

All operations require:
- Valid user session with JWT token
- User with "inventory" module permission
- User ID for audit trail

---

## 📞 Common Questions

### Q: Can I deduct multiple items at once?
**A:** Yes! Use `deduct_multiple_items()` - See example #5 above.

### Q: What if I don't have enough stock?
**A:** You'll get an `HTTPException(400)` with details about the shortage. Pre-check with `is_stock_available()` to avoid this.

### Q: How are costs calculated?
**A:** FIFO (First-In-First-Out). Oldest batches are used first, cost is weighted average across batches used.

### Q: Can I see which batches were used?
**A:** Yes! The `deduct_stock()` result includes a `batches_used` array with full details.

### Q: Can I track costs per tank?
**A:** Yes! Use `get_consumption_report()` with `reference_id=tank_id` to filter by tank.

### Q: What if an item expires?
**A:** Check daily with `get_expiring_items(days=30)` to see what's expiring soon.

### Q: Can I undo a deduction?
**A:** No automatic undo. Use stock adjustments (`POST /api/v1/inventory/stock/adjust`) to manually correct if needed.

---

## 🚀 Ready to Go!

You now have everything you need to integrate biofloc with inventory. Start with the copy & paste template at the top, then explore the full examples as needed.

**Happy farming! 🐟🌱**

---

_Last updated: 2025-11-18_
