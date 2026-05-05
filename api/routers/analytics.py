"""
Real-time Analytics Dashboard API for Carbon Trace Kenya
Provides emissions analytics, trends, and insights
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from db.session import get_db
from carbontrace.models import Company, EmissionRecord, Document
from api.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Schemas
class EmissionTrend(BaseModel):
    date: str
    scope1: float
    scope2: float
    scope3: float
    total: float

class TopEmitter(BaseModel):
    company_id: int
    company_name: str
    total_emissions: float
    trend: str  # 'up', 'down', 'stable'

class SectorComparison(BaseModel):
    sector: str
    avg_emissions: float
    company_count: int
    top_performer: str

class AnomalyDetection(BaseModel):
    record_id: int
    company_name: str
    anomaly_type: str
    severity: str  # 'high', 'medium', 'low'
    description: str
    detected_at: datetime

class DashboardSummary(BaseModel):
    total_companies: int
    total_emissions_today: float
    avg_emissions_per_company: float
    anomaly_count_24h: int
    trend_direction: str  # 'increasing', 'decreasing', 'stable'


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get real-time dashboard summary statistics"""
    
    # Total companies
    total_companies = db.query(Company).count()
    
    # Today's emissions
    today = datetime.utcnow().date()
    today_emissions = db.query(
        func.sum(EmissionRecord.total_emissions)
    ).filter(
        func.date(EmissionRecord.reporting_date) == today
    ).scalar() or 0.0
    
    # Average emissions per company (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    avg_emissions = db.query(
        func.avg(EmissionRecord.total_emissions)
    ).filter(
        EmissionRecord.reporting_date >= thirty_days_ago
    ).scalar() or 0.0
    
    # Anomalies in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    anomaly_count = db.query(Document).filter(
        Document.anomaly_detected == True,
        Document.created_at >= twenty_four_hours_ago
    ).count()
    
    # Trend direction (compare last 7 days to previous 7 days)
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)
    
    recent_emissions = db.query(
        func.sum(EmissionRecord.total_emissions)
    ).filter(
        EmissionRecord.reporting_date >= seven_days_ago
    ).scalar() or 0.0
    
    previous_emissions = db.query(
        func.sum(EmissionRecord.total_emissions)
    ).filter(
        EmissionRecord.reporting_date >= fourteen_days_ago,
        EmissionRecord.reporting_date < seven_days_ago
    ).scalar() or 0.0
    
    if previous_emissions == 0:
        trend = 'stable'
    else:
        change_pct = (recent_emissions - previous_emissions) / previous_emissions * 100
        if change_pct > 5:
            trend = 'increasing'
        elif change_pct < -5:
            trend = 'decreasing'
        else:
            trend = 'stable'
    
    return DashboardSummary(
        total_companies=total_companies,
        total_emissions_today=round(today_emissions, 2),
        avg_emissions_per_company=round(avg_emissions, 2),
        anomaly_count_24h=anomaly_count,
        trend_direction=trend
    )


@router.get("/emissions/trend", response_model=List[EmissionTrend])
async def get_emissions_trend(
    days: int = Query(default=30, ge=7, le=365),
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get emissions trend over time"""
    
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    query = db.query(
        func.date(EmissionRecord.reporting_date).label('date'),
        func.sum(EmissionRecord.scope1_emissions).label('scope1'),
        func.sum(EmissionRecord.scope2_emissions).label('scope2'),
        func.sum(EmissionRecord.scope3_emissions).label('scope3'),
        func.sum(EmissionRecord.total_emissions).label('total')
    ).filter(
        EmissionRecord.reporting_date >= start_date
    )
    
    if company_id:
        query = query.filter(EmissionRecord.company_id == company_id)
    
    results = query.group_by(
        func.date(EmissionRecord.reporting_date)
    ).order_by('date').all()
    
    return [
        EmissionTrend(
            date=str(r.date),
            scope1=round(r.scope1 or 0, 2),
            scope2=round(r.scope2 or 0, 2),
            scope3=round(r.scope3 or 0, 2),
            total=round(r.total or 0, 2)
        )
        for r in results
    ]


@router.get("/companies/top-emitters", response_model=List[TopEmitter])
async def get_top_emitters(
    limit: int = Query(default=10, ge=1, le=50),
    period: str = Query(default="30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get top emitting companies"""
    
    days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}[period]
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    results = db.query(
        Company.id,
        Company.name,
        func.sum(EmissionRecord.total_emissions).label('total_emissions')
    ).join(
        EmissionRecord
    ).filter(
        EmissionRecord.reporting_date >= start_date
    ).group_by(
        Company.id,
        Company.name
    ).order_by(
        desc('total_emissions')
    ).limit(limit).all()
    
    # Calculate trends for each company
    emitters = []
    for r in results:
        # Compare current period to previous period
        current_start = datetime.utcnow().date() - timedelta(days=days)
        previous_start = current_start - timedelta(days=days)
        
        current_total = db.query(
            func.sum(EmissionRecord.total_emissions)
        ).filter(
            EmissionRecord.company_id == r.id,
            EmissionRecord.reporting_date >= current_start
        ).scalar() or 0.0
        
        previous_total = db.query(
            func.sum(EmissionRecord.total_emissions)
        ).filter(
            EmissionRecord.company_id == r.id,
            EmissionRecord.reporting_date >= previous_start,
            EmissionRecord.reporting_date < current_start
        ).scalar() or 0.0
        
        if previous_total == 0:
            trend = 'stable'
        elif current_total > previous_total * 1.05:
            trend = 'up'
        elif current_total < previous_total * 0.95:
            trend = 'down'
        else:
            trend = 'stable'
        
        emitters.append(TopEmitter(
            company_id=r.id,
            company_name=r.name,
            total_emissions=round(r.total_emissions or 0, 2),
            trend=trend
        ))
    
    return emitters


@router.get("/sectors/comparison", response_model=List[SectorComparison])
async def get_sector_comparison(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Compare emissions across sectors"""
    
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    
    results = db.query(
        Company.sector,
        func.avg(EmissionRecord.total_emissions).label('avg_emissions'),
        func.count(Company.id.distinct()).label('company_count')
    ).join(
        EmissionRecord
    ).filter(
        EmissionRecord.reporting_date >= thirty_days_ago
    ).group_by(
        Company.sector
    ).all()
    
    sectors = []
    for r in results:
        # Find top performer (lowest emissions) in this sector
        top_company = db.query(
            Company.name
        ).join(
            EmissionRecord
        ).filter(
            Company.sector == r.sector,
            EmissionRecord.reporting_date >= thirty_days_ago
        ).group_by(
            Company.id,
            Company.name
        ).order_by(
            func.sum(EmissionRecord.total_emissions)
        ).first()
        
        sectors.append(SectorComparison(
            sector=r.sector or 'Unknown',
            avg_emissions=round(r.avg_emissions or 0, 2),
            company_count=r.company_count,
            top_performer=top_company[0] if top_company else 'N/A'
        ))
    
    return sectors


@router.get("/anomalies/recent", response_model=List[AnomalyDetection])
async def get_recent_anomalies(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent anomaly detections"""
    
    results = db.query(
        Document.id,
        Company.name.label('company_name'),
        Document.anomaly_type,
        Document.anomaly_severity,
        Document.anomaly_description,
        Document.created_at
    ).join(
        Company, Document.company_id == Company.id
    ).filter(
        Document.anomaly_detected == True
    ).order_by(
        desc(Document.created_at)
    ).limit(limit).all()
    
    return [
        AnomalyDetection(
            record_id=r.id,
            company_name=r.company_name,
            anomaly_type=r.anomaly_type or 'Unknown',
            severity=r.anomaly_severity or 'medium',
            description=r.anomaly_description or 'Anomaly detected in emissions data',
            detected_at=r.created_at
        )
        for r in results
    ]


@router.get("/emissions/forecast")
async def get_emissions_forecast(
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Simple emissions forecast based on historical trends
    (In production, this would use ML models)
    """
    
    # Get last 60 days for trend calculation
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=60)
    
    historical = db.query(
        func.date(EmissionRecord.reporting_date).label('date'),
        func.sum(EmissionRecord.total_emissions).label('emissions')
    ).filter(
        EmissionRecord.reporting_date >= start_date
    ).group_by(
        func.date(EmissionRecord.reporting_date)
    ).order_by('date').all()
    
    if len(historical) < 7:
        return {"forecast": [], "confidence": 0.0, "message": "Insufficient data for forecast"}
    
    # Calculate 7-day moving average trend
    emissions_values = [h.emissions for h in historical]
    recent_avg = sum(emissions_values[-7:]) / 7
    previous_avg = sum(emissions_values[-14:-7]) / 7
    
    trend = recent_avg - previous_avg
    
    # Generate forecast
    forecast = []
    last_date = datetime.strptime(str(historical[-1].date), '%Y-%m-%d').date()
    last_value = emissions_values[-1]
    
    for i in range(1, days + 1):
        forecast_date = last_date + timedelta(days=i)
        # Add trend with some randomness
        predicted_value = max(0, last_value + trend + (trend * 0.1 * (i % 3 - 1)))
        
        forecast.append({
            'date': forecast_date.isoformat(),
            'predicted_emissions': round(predicted_value, 2),
            'confidence': max(0.5, 0.95 - (i * 0.01))  # Decreasing confidence over time
        })
        
        last_value = predicted_value
    
    return {
        "forecast": forecast,
        "confidence": 0.75,
        "trend": "increasing" if trend > 0 else "decreasing",
        "trend_value": round(abs(trend), 2)
    }
