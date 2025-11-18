"""
Simple migration runner for biofloc module
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import connect_db, disconnect_db, pool
import asyncpg


async def run_migration():
    """Run the biofloc migration SQL file"""
    print("🚀 Starting biofloc module migration...")

    # Connect to database
    await connect_db()

    try:
        # Read migration file
        migration_file = Path(__file__).parent / "migrations" / "biofloc_module_v1.0.0.sql"

        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False

        print(f"📄 Reading migration file: {migration_file}")
        sql_content = migration_file.read_text()

        # Execute migration
        print("⚙️  Executing migration...")
        async with pool.acquire() as conn:
            # Execute the entire SQL file
            await conn.execute(sql_content)

        print("✅ Migration completed successfully!")

        # Verify tables were created
        async with pool.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE 'biofloc_%'
                ORDER BY table_name
                """
            )

            print(f"\n📊 Created {len(result)} biofloc tables:")
            for row in result:
                print(f"   - {row['table_name']}")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Disconnect from database
        await disconnect_db()


if __name__ == "__main__":
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)
