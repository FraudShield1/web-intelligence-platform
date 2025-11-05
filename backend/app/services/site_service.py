"""Site service - business logic for site operations"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse, SiteListResponse

logger = logging.getLogger(__name__)


class SiteService:
    """Service for site operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_site(self, site_data: SiteCreate) -> SiteResponse:
        """Create a new site"""
        logger.info(f"Creating site: {site_data.domain}")
        
        # Create site instance
        db_site = Site(
            domain=site_data.domain,
            business_value_score=site_data.business_value_score,
            notes=site_data.notes,
            status="pending"
        )
        
        self.db.add(db_site)
        await self.db.commit()
        await self.db.refresh(db_site)
        
        logger.info(f"Site created: {db_site.site_id}")
        return SiteResponse.from_orm(db_site)

    async def get_site(self, site_id: UUID) -> Optional[SiteResponse]:
        """Get a site by ID"""
        result = await self.db.execute(
            select(Site).where(Site.site_id == site_id)
        )
        site = result.scalar_one_or_none()
        if site:
            return SiteResponse.from_orm(site)
        return None

    async def list_sites(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "-created_at"
    ) -> SiteListResponse:
        """List sites with filters and pagination"""
        query = select(Site)

        # Apply filters
        if status:
            query = query.where(Site.status == status)
        if platform:
            query = query.where(Site.platform == platform)
        if search:
            query = query.where(Site.domain.contains(search))

        # Get total count
        count_result = await self.db.execute(select(func.count(Site.site_id)).select_from(Site))
        total = count_result.scalar()

        # Apply sorting
        if sort_by.startswith("-"):
            # Descending
            sort_column = getattr(Site, sort_by[1:], Site.created_at)
            query = query.order_by(sort_column.desc())
        else:
            # Ascending
            sort_column = getattr(Site, sort_by, Site.created_at)
            query = query.order_by(sort_column)

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await self.db.execute(query)
        sites = result.scalars().all()

        return SiteListResponse(
            total=total,
            limit=limit,
            offset=offset,
            sites=[SiteResponse.from_orm(site) for site in sites]
        )

    async def update_site(self, site_id: UUID, site_data: SiteUpdate) -> Optional[SiteResponse]:
        """Update a site"""
        result = await self.db.execute(
            select(Site).where(Site.site_id == site_id)
        )
        db_site = result.scalar_one_or_none()
        
        if not db_site:
            return None

        # Update fields if provided
        update_data = site_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_site, field, value)

        await self.db.commit()
        await self.db.refresh(db_site)
        
        logger.info(f"Site updated: {db_site.site_id}")
        return SiteResponse.from_orm(db_site)

    async def delete_site(self, site_id: UUID) -> bool:
        """Delete a site"""
        result = await self.db.execute(
            select(Site).where(Site.site_id == site_id)
        )
        db_site = result.scalar_one_or_none()
        
        if not db_site:
            return False

        await self.db.delete(db_site)
        await self.db.commit()
        
        logger.info(f"Site deleted: {site_id}")
        return True

    async def get_site_by_domain(self, domain: str) -> Optional[Site]:
        """Get site by domain name"""
        result = await self.db.execute(
            select(Site).where(Site.domain == domain)
        )
        return result.scalar_one_or_none()

