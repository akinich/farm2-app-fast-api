"""
System Settings Models
Version: 1.0.0
Description: Pydantic models for system settings and configuration
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from datetime import datetime

class SystemSettingSchema(BaseModel):
    """System setting model"""
    setting_key: str
    setting_value: Any
    data_type: str = Field(..., pattern="^(string|integer|float|boolean|json)$")
    category: str
    description: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    is_public: bool = False
    is_encrypted: bool = False

    class Config:
        from_attributes = True

class SystemSettingResponse(SystemSettingSchema):
    """System setting response with metadata"""
    id: int
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SettingUpdateRequest(BaseModel):
    """Request to update a setting"""
    setting_value: Any

class SettingsByCategoryResponse(BaseModel):
    """Settings grouped by category"""
    category: str
    settings: list[SystemSettingResponse]

class SettingsAuditLogResponse(BaseModel):
    """Audit log entry for settings changes"""
    id: int
    setting_key: str
    old_value: Any
    new_value: Any
    changed_by: str
    changed_at: datetime

    class Config:
        from_attributes = True
