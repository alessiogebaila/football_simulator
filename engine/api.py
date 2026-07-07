"""FastAPI router exposing the prediction engine.

Mounted by backend_simple.py under /engine.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import predict as engine_predict
from .config import DB_PATH

router = APIRouter(prefix="/engine", tags=["prediction-engine"])


class OddsInput(BaseModel):
    home: Optional[float] = None
    draw: Optional[float] = None
    away: Optional[float] = None


class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    scope: str = "club"  # 'club' | 'international'
    neutral: bool = False
    bookmaker_odds: Optional[OddsInput] = None
    home_lineup: Optional[list[str]] = None  # confirmed starting XI names
    away_lineup: Optional[list[str]] = None


@router.get("/status")
async def status():
    return {
        "engine": "ready" if DB_PATH.exists() else "no data - run: python -m engine.ingest",
        "database": str(DB_PATH),
    }


@router.get("/teams")
async def teams():
    try:
        return engine_predict.list_teams()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/predict")
async def predict(req: PredictRequest):
    if req.scope not in ("club", "international"):
        raise HTTPException(status_code=400, detail="scope must be 'club' or 'international'")
    odds = None
    if req.bookmaker_odds:
        odds = {k: v for k, v in req.bookmaker_odds.model_dump().items() if v}
    try:
        return engine_predict.predict_match(
            req.home_team, req.away_team,
            scope=req.scope, neutral=req.neutral, bookmaker_odds=odds,
            home_lineup=req.home_lineup, away_lineup=req.away_lineup,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc.args[0]))


@router.get("/backtest")
async def backtest_results():
    path = Path("engine/data/backtest_results.json")
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="No backtest results yet - run: python -m engine.backtest",
        )
    return json.loads(path.read_text(encoding="utf-8"))
