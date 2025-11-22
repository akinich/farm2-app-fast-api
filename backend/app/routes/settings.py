"""
================================================================================
Farm Management System - Settings & Configuration Routes
================================================================================
Version: 1.0.0
Last Updated: 2025-11-22

Changelog:
----------
v1.0.0 (2025-11-22):
  - Initial settings management endpoints
  - CRUD operations for system settings
  - Settings by category
  - Audit log tracking
  - Caching support
  - Admin-only access

================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import logging

from app.schemas.auth import CurrentUser
from app.auth.dependencies import require_admin
from app.models.settings import (
    SystemSettingResponse,
    SettingUpdateRequest,
    SettingsByCategoryResponse,
    SettingsAuditLogResponse
)
from app.services import settings_service
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# SETTINGS ENDPOINTS
# ============================================================================


@router.get(
    "/",
    response_model=List[SystemSettingResponse],
    summary="Get All Settings",
    description="Get all system settings (Admin only)"
)
async def get_all_settings(
    current_user: CurrentUser = Depends(require_admin),
):
    """Get all system settings (Admin only)"""
    try:
        pool = get_db()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    id, setting_key, setting_value, data_type, category,
                    description, validation_rules, is_public, is_encrypted,
                    updated_by, created_at, updated_at
                FROM system_settings
                ORDER BY category, setting_key
                """
            )
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to fetch settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch settings"
        )


@router.get(
    "/public",
    response_model=Dict[str, Any],
    summary="Get Public Settings",
    description="Get public settings (accessible to all authenticated users)"
)
async def get_public_settings(
    current_user: CurrentUser = Depends(require_admin),
):
    """Get public settings (accessible to all authenticated users)"""
    try:
        pool = get_db()
        async with pool.acquire() as conn:
            return await settings_service.get_public_settings(conn)
    except Exception as e:
        logger.error(f"Failed to fetch public settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch public settings"
        )


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get Setting Categories",
    description="Get list of all setting categories"
)
async def get_categories(
    current_user: CurrentUser = Depends(require_admin),
):
    """Get list of setting categories"""
    try:
        pool = get_db()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT DISTINCT category FROM system_settings ORDER BY category"
            )
            return [row['category'] for row in rows]
    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


@router.get(
    "/category/{category}",
    response_model=List[SystemSettingResponse],
    summary="Get Settings By Category",
    description="Get all settings in a specific category"
)
async def get_settings_by_category(
    category: str,
    current_user: CurrentUser = Depends(require_admin),
):
    """Get all settings in a specific category"""
    try:
        pool = get_db()
        async with pool.acquire() as conn:
            settings = await settings_service.get_settings_by_category(conn, category)
            return settings
    except Exception as e:
        logger.error(f"Failed to fetch settings for category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch settings for category: {category}"
        )


@router.put(
    "/{setting_key}",
    response_model=SystemSettingResponse,
    summary="Update Setting",
    description="Update a setting value with validation"
)
async def update_setting(
    setting_key: str,
    request: SettingUpdateRequest,
    current_user: CurrentUser = Depends(require_admin),
):
    """Update a setting value"""
    try:
        pool = get_db()
        async with pool.acquire() as conn:
            updated = await settings_service.update_setting(
                conn,
                setting_key,
                request.setting_value,
                current_user.id
            )
            logger.info(f"Setting '{setting_key}' updated by user {current_user.email}")
            return updated
    except ValueError as e:
        logger.warning(f"Validation error updating setting {setting_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update setting {setting_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update setting: {setting_key}"
        )


@router.get(
    "/audit-log",
    response_model=List[SettingsAuditLogResponse],
    summary="Get Audit Log",
    description="Get settings change audit log"
)
async def get_audit_log(
    setting_key: Optional[str] = None,
    limit: int = 100,
    current_user: CurrentUser = Depends(require_admin),
):
    """Get settings change audit log"""
    try:
        pool = get_db()
        async with pool.acquire() as conn:
            logs = await settings_service.get_audit_log(conn, setting_key, limit)
            return logs
    except Exception as e:
        logger.error(f"Failed to fetch audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch audit log"
        )
