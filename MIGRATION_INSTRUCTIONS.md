# Database Migration Instructions

## CRITICAL: Fix Biofloc Feeding Inventory Deduction Error

### Problem
Biofloc feeding sessions fail with error:
```
invalid input for query argument $8: UUID('...') (value out of int32 range)
```

### Root Cause
- `inventory_transactions.tank_id` column is INTEGER type
- Biofloc tanks use UUID for IDs
- Cannot insert UUID into INTEGER column

### Solution
Run migration v1.3.1 to change `tank_id` from INTEGER to UUID.

---

## Migration Steps

### Option 1: Supabase Dashboard (Recommended for Render deployments)

1. **Open Supabase SQL Editor**:
   - Go to your Supabase project dashboard
   - Navigate to "SQL Editor" in the left menu
   - Click "New Query"

2. **Copy Migration SQL**:
   - Open `sql_scripts/v1.3.1_fix_tank_id_uuid.sql`
   - Copy the entire contents

3. **Run Migration**:
   - Paste the SQL into the editor
   - Click "Run" or press Ctrl+Enter
   - Wait for completion (should take < 5 seconds)

4. **Verify Success**:
   - Check for green success message
   - Look for migration completion notices in the results panel

5. **Restart Backend**:
   - Go to Render dashboard
   - Find your backend service
   - Click "Manual Deploy" → "Clear build cache & deploy"
   - Wait 2-5 minutes for deployment

---

## Verification

After running the migration, test feeding session:
1. Go to biofloc/feeding page
2. Select a tank with an active batch
3. Add feed items (e.g., FF01, FF02)
4. Submit feeding session
5. **Should succeed** with "Feeding session recorded successfully"

---

## Frontend Routing Fix (Render)

The frontend 404 error requires Render configuration:

1. Go to Render dashboard → Your frontend service
2. Navigate to "Redirects/Rewrites" section
3. Add this rewrite rule:
   - Source: `/*`
   - Destination: `/index.html`
   - Action: `Rewrite`
4. Save and redeploy

This fixes the `/login` 404 error by ensuring all routes serve index.html.

---

## Migration Timeline

- **v1.0.0**: Initial schema with `tank_id INTEGER`
- **v1.3.0**: Added biofloc integration fields
- **v1.3.1**: **Fixed `tank_id` to UUID** ← You are here
