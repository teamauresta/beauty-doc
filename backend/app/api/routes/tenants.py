from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

router = APIRouter()


class TenantCreate(BaseModel):
    """Schema for creating a new tenant (医美机构)."""
    name: str  # 机构名称
    city: str  # 城市
    tier: str  # 客单价层级: high/medium/low
    main_services: list[str]  # 主打项目
    target_audience: Optional[str] = None  # 客群画像
    competitors: Optional[list[str]] = None  # 竞品


class TenantResponse(BaseModel):
    """Response schema for tenant."""
    id: UUID
    name: str
    city: str
    tier: str
    main_services: list[str]
    target_audience: Optional[str]
    competitors: Optional[list[str]]
    created_at: datetime


# In-memory storage for MVP (replace with database)
_tenants: dict[UUID, TenantResponse] = {}


@router.post("/", response_model=TenantResponse)
async def create_tenant(tenant: TenantCreate) -> TenantResponse:
    """Create a new tenant (医美机构)."""
    tenant_id = uuid4()
    response = TenantResponse(
        id=tenant_id,
        name=tenant.name,
        city=tenant.city,
        tier=tenant.tier,
        main_services=tenant.main_services,
        target_audience=tenant.target_audience,
        competitors=tenant.competitors,
        created_at=datetime.utcnow(),
    )
    _tenants[tenant_id] = response
    return response


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: UUID) -> TenantResponse:
    """Get tenant by ID."""
    if tenant_id not in _tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return _tenants[tenant_id]


@router.get("/", response_model=list[TenantResponse])
async def list_tenants() -> list[TenantResponse]:
    """List all tenants."""
    return list(_tenants.values())
