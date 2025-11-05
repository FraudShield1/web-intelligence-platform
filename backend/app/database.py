"""Database connection and session management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import ssl

Base = declarative_base()

# Parse DATABASE_URL and remove sslmode parameter if present
database_url = settings.DATABASE_URL
connect_args = {}

# For asyncpg, handle SSL properly
if "sslmode=" in database_url:
    # Remove sslmode from URL
    database_url = database_url.split("?")[0]
    # asyncpg requires ssl context object, not sslmode string
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

# Create async engine
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

async def get_db():
    """Dependency for getting database session"""
    async with async_session_maker() as session:
        yield session

async def init_db():
    """Initialize database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Close database connection"""
    await engine.dispose()
