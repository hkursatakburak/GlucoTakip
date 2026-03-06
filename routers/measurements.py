from fastapi import APIRouter, Depends, Request, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import crud, schemas, database, models, i18n
from routers.auth import get_current_user_from_cookie

router = APIRouter(tags=["Measurements"])
templates = Jinja2Templates(directory="templates")
i18n.setup_templates(templates)

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    measurements = crud.get_measurements(db, user_id=user.id)
    
    chart_data = [
        {
            "date": m.measured_at.strftime("%Y-%m-%d %H:%M"),
            "value": m.value
        } for m in reversed(measurements[:30]) # Show up to 30 last measurements in chart
    ]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "measurements": measurements,
        "chart_data": chart_data
    })

@router.get("/add-measurement", response_class=HTMLResponse)
async def add_measurement_page(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add_measurement.html", {
        "request": request,
        "user": user,
        "categories": [c.value for c in models.MeasurementCategory]
    })

@router.post("/add-measurement")
async def add_measurement(
    request: Request,
    value: int = Form(...),
    measured_at: str = Form(...),
    category: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(database.get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Expected format from HTML5 datetime-local is YYYY-MM-DDTHH:MM
        parsed_date = datetime.strptime(measured_at, "%Y-%m-%dT%H:%M")
    except ValueError:
        parsed_date = datetime.utcnow()
        
    measurement_schema = schemas.MeasurementCreate(
        value=value,
        measured_at=parsed_date,
        category=models.MeasurementCategory(category),
        notes=notes
    )
    crud.create_measurement(db=db, measurement=measurement_schema, user_id=user.id)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
