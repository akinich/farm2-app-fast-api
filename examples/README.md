# Farm Management System - Examples

This directory contains example code demonstrating how to use various modules and integrations in the Farm Management System.

## Available Examples

### `biofloc_inventory_examples.py`

Comprehensive examples showing how to integrate the biofloc module with the inventory system.

**Includes:**
- Daily feeding operations with stock deduction
- Multi-item feeding schedules
- Water quality management with chemical usage
- Stock level monitoring and alerts
- Consumption reporting and analytics
- Error handling patterns
- Complete daily workflow examples

**How to Use:**

```python
# Import specific examples
from examples.biofloc_inventory_examples import (
    example_daily_feeding,
    example_feeding_schedule,
    example_check_stock_before_feeding,
    example_monthly_consumption_report
)

# Run an example
await example_daily_feeding(tank_id="tank-001", user_id="user-uuid")

# Or run all examples
from examples.biofloc_inventory_examples import run_all_examples
await run_all_examples()
```

**Available Examples:**

1. **example_daily_feeding** - Basic stock deduction for feeding
2. **example_feeding_schedule** - Deduct multiple items at once
3. **example_water_treatment** - Chemical usage for water management
4. **example_check_stock_before_feeding** - Pre-operation stock validation
5. **example_monitor_low_stock** - Daily low stock monitoring
6. **example_check_expiring_items** - Expiry alert checking
7. **example_monthly_consumption_report** - Monthly cost analysis
8. **example_tank_transaction_history** - Tank-specific audit trail
9. **example_get_feed_items** - List items by category
10. **example_daily_operations_workflow** - Complete daily routine
11. **example_error_handling** - Error handling best practices

## Quick Start

### Prerequisites

1. Inventory module must be set up and populated with items
2. User must have inventory module permissions
3. Database must be running and accessible

### Running Examples

**Option 1: Import in your code**

```python
from app.helpers.inventory_integration import InventoryIntegration

inv = InventoryIntegration(module_name="biofloc")
result = await inv.deduct_stock(
    item_sku="FEED-PELLET-5MM",
    quantity=10.5,
    user_id=user_id,
    reference_id=tank_id
)
```

**Option 2: Run example script**

```bash
# From project root
cd backend
python -m examples.biofloc_inventory_examples
```

**Option 3: Interactive Python shell**

```bash
cd backend
python

>>> from examples.biofloc_inventory_examples import *
>>> import asyncio
>>> asyncio.run(example_daily_feeding("tank-001", "user-uuid"))
```

## Documentation

For detailed integration guide, see:
- `/docs/BIOFLOC_INVENTORY_QUICKSTART.md` - 5-minute quick start
- `/docs/INVENTORY_INTEGRATION_GUIDE.md` - Complete integration guide

## Contributing Examples

When adding new examples:

1. Create a new Python file: `examples/[module]_[feature]_examples.py`
2. Add comprehensive docstrings to each function
3. Include error handling demonstrations
4. Update this README with the new examples
5. Add entry to main project README

### Example Template

```python
async def example_your_feature(param1: str, param2: str):
    \"\"\"
    Example: Brief description of what this demonstrates.

    Use case: When would someone use this?
    \"\"\"
    # Your example code here
    pass
```

## Support

For questions or issues with examples:
1. Check the documentation in `/docs/`
2. Review the source code in `/backend/app/helpers/`
3. Contact the development team

---

_Last updated: 2025-11-18_
