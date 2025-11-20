"""Database connection pool for PostgreSQL"""
import asyncpg
from typing import Optional
from .config import settings


class DatabasePool:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        print(f"✓ Database pool created: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("✓ Database pool closed")
    
    async def execute_query(self, query: str, params: list = None):
        """Execute SELECT query and return results"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            if params:
                records = await conn.fetch(query, *params)
            else:
                records = await conn.fetch(query)
            
            return [dict(record) for record in records]


# Global database pool instance
db_pool = DatabasePool()
