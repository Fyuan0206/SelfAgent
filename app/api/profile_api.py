"""
用户画像管理 API
读取 profiles/ 目录中的用户画像 JSON 文件
"""

import os
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger

from app.core.auth import get_current_admin


router = APIRouter(prefix="/api/v1/admin", tags=["用户画像管理"])

# Profiles directory path
PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "profiles")


# ==================== Response Models ====================

class ProfileSummary(BaseModel):
    """用户画像摘要"""
    user_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    total_interactions: int = 0
    crisis_count: int = 0
    intervention_count: int = 0
    data_quality_score: float = 0.0


class ProfileDetail(BaseModel):
    """用户画像详情"""
    user_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    total_interactions: int = 0
    crisis_count: int = 0
    intervention_count: int = 0
    avg_recovery_time: float = 0.0
    data_quality_score: float = 0.0
    emotion_baseline: dict = {}
    emotion_trend: dict = {}
    personality: dict = {}
    risk_prediction: dict = {}
    snapshots: List[dict] = []


class DashboardStats(BaseModel):
    """仪表板统计"""
    total_profiles: int = 0
    total_interactions: int = 0
    total_crisis: int = 0
    total_interventions: int = 0
    avg_data_quality: float = 0.0


# ==================== Helper Functions ====================

def read_profile_file(filename: str) -> Optional[dict]:
    """读取单个画像文件"""
    filepath = os.path.join(PROFILES_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read profile {filename}: {e}")
        return None


def get_all_profile_files() -> List[str]:
    """获取所有画像文件名"""
    if not os.path.exists(PROFILES_DIR):
        logger.warning(f"Profiles directory not found: {PROFILES_DIR}")
        return []

    files = []
    for f in os.listdir(PROFILES_DIR):
        # Skip hidden files and non-json files
        if f.startswith('.') or f.startswith('._') or not f.endswith('.json'):
            continue
        # Skip None.json (invalid user)
        if f == 'None.json':
            continue
        files.append(f)
    return files


# ==================== API Endpoints ====================

@router.get("/profiles", response_model=List[ProfileSummary])
async def list_profiles(
    _: bool = Depends(get_current_admin)
) -> List[ProfileSummary]:
    """
    获取所有用户画像列表

    返回画像摘要信息，包括用户ID、互动次数、危机次数等
    """
    profiles = []

    for filename in get_all_profile_files():
        data = read_profile_file(filename)
        if not data:
            continue

        profiles.append(ProfileSummary(
            user_id=data.get('user_id', filename.replace('.json', '')),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            total_interactions=data.get('total_interactions', 0),
            crisis_count=data.get('crisis_count', 0),
            intervention_count=data.get('intervention_count', 0),
            data_quality_score=data.get('data_quality_score', 0.0)
        ))

    # Sort by updated_at descending
    profiles.sort(key=lambda p: p.updated_at or '', reverse=True)

    return profiles


@router.get("/profiles/{user_id}", response_model=ProfileDetail)
async def get_profile(
    user_id: str,
    _: bool = Depends(get_current_admin)
) -> ProfileDetail:
    """
    获取单个用户画像详情

    - **user_id**: 用户ID
    """
    filename = f"{user_id}.json"
    data = read_profile_file(filename)

    if not data:
        raise HTTPException(status_code=404, detail="用户画像不存在")

    return ProfileDetail(
        user_id=data.get('user_id', user_id),
        created_at=data.get('created_at'),
        updated_at=data.get('updated_at'),
        total_interactions=data.get('total_interactions', 0),
        crisis_count=data.get('crisis_count', 0),
        intervention_count=data.get('intervention_count', 0),
        avg_recovery_time=data.get('avg_recovery_time', 0.0),
        data_quality_score=data.get('data_quality_score', 0.0),
        emotion_baseline=data.get('emotion_baseline', {}),
        emotion_trend=data.get('emotion_trend', {}),
        personality=data.get('personality', {}),
        risk_prediction=data.get('risk_prediction', {}),
        snapshots=data.get('snapshots', [])[-10:]  # Only return last 10 snapshots
    )


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    _: bool = Depends(get_current_admin)
) -> DashboardStats:
    """
    获取仪表板统计数据

    汇总所有用户画像的统计信息
    """
    total_profiles = 0
    total_interactions = 0
    total_crisis = 0
    total_interventions = 0
    total_quality = 0.0

    for filename in get_all_profile_files():
        data = read_profile_file(filename)
        if not data:
            continue

        total_profiles += 1
        total_interactions += data.get('total_interactions', 0)
        total_crisis += data.get('crisis_count', 0)
        total_interventions += data.get('intervention_count', 0)
        total_quality += data.get('data_quality_score', 0.0)

    return DashboardStats(
        total_profiles=total_profiles,
        total_interactions=total_interactions,
        total_crisis=total_crisis,
        total_interventions=total_interventions,
        avg_data_quality=total_quality / total_profiles if total_profiles > 0 else 0.0
    )
