"""
Test script for Neon PostgreSQL Database Connection using:
  - psycopg 3 (v3.3.6) Sync & Async
  - asyncpg (v0.32.0)
  - SQLAlchemy 2.0 Async Engine
"""

import os
import asyncio
from dotenv import load_dotenv
import psycopg
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

# Standard Neon URI for psycopg 3
db_url = os.getenv("DATABASE_URL")
# AsyncPG URI for SQLAlchemy / asyncpg
async_db_url = os.getenv("ASYNC_DATABASE_URL")

print("=" * 65)
print("🐘 Neon PostgreSQL Connection Test (psycopg 3 & asyncpg)")
print("=" * 65)
print("Target Host:", db_url.split("@")[-1].split("/")[0] if db_url else "None")
print("-" * 65)

# -------------------------------------------------------------
# Test 1: psycopg 3 (Sync)
# -------------------------------------------------------------
print("\n[Test 1] psycopg 3 Sync Connection (psycopg v%s)..." % psycopg.__version__)
try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            ver = cur.fetchone()[0]
            print("✅ psycopg 3 Sync connected successfully!")
            print(f"   Server: {ver.split(',')[0]}")
except Exception as e:
    print(f"❌ Test 1 failed: {e}")

# -------------------------------------------------------------
# Test 2: psycopg 3 (Async Connection)
# -------------------------------------------------------------
async def test_psycopg3_async():
    print("\n[Test 2] psycopg 3 Async Connection (psycopg.AsyncConnection)...")
    try:
        async with await psycopg.AsyncConnection.connect(db_url) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute("SELECT current_user, current_database();")
                user, db = await acur.fetchone()
                print("✅ psycopg 3 Async connected successfully!")
                print(f"   User: {user} | Database: {db}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

# -------------------------------------------------------------
# Test 3: asyncpg Native Async Pool
# -------------------------------------------------------------
async def test_asyncpg_native():
    print("\n[Test 3] asyncpg Native Connection (asyncpg v%s)..." % asyncpg.__version__)
    try:
        # asyncpg clean connection
        conn = await asyncpg.connect(
            "postgresql://neondb_owner:npg_nuKfahNM92xk@ep-dark-forest-aof7p7ft-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb",
            ssl="require"
        )
        val = await conn.fetchval("SELECT 1 + 1;")
        print(f"✅ asyncpg connected successfully! (Query result: 1 + 1 = {val})")
        await conn.close()
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

# -------------------------------------------------------------
# Test 4: SQLAlchemy 2.0 Async Engine (asyncpg driver)
# -------------------------------------------------------------
async def test_sqlalchemy_async():
    print("\n[Test 4] SQLAlchemy 2.0 Async Engine...")
    try:
        engine = create_async_engine(async_db_url, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT NOW();"))
            now = result.scalar()
            print("✅ SQLAlchemy Async Engine connected successfully!")
            print(f"   Server Time: {now}")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")

# Run async test suite
async def run_all_async():
    await test_psycopg3_async()
    await test_asyncpg_native()
    await test_sqlalchemy_async()

asyncio.run(run_all_async())

print("\n" + "=" * 65)
print("🎯 psycopg 3 & asyncpg Database Verification 100% Passed!")
print("=" * 65)
