from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import crud, database
from routers.auth import get_current_user_from_cookie
import pandas as pd
import os

router = APIRouter(tags=["Reports"])

@router.post("/export")
async def export_data(
    request: Request,
    date_range: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
    end_date = datetime.utcnow()
    if date_range == "7":
        start_date = end_date - timedelta(days=7)
    elif date_range == "30":
        start_date = end_date - timedelta(days=30)
    elif date_range == "90":
        start_date = end_date - timedelta(days=90)
    else:
        # Default all time
        start_date = end_date - timedelta(days=3650)
        
    measurements = crud.get_measurements_by_date_range(db, user.id, start_date, end_date)
    
    lang = i18n.get_language(request)
    
    val_header = i18n.get_translation("admin.table_value", lang)
    cat_header = i18n.get_translation("admin.table_category", lang)
    date_header = i18n.get_translation("admin.table_date", lang)
    notes_header = i18n.get_translation("add_measurement.notes_label", lang)

    data = []
    for m in measurements:
        data.append({
            date_header: m.measured_at.strftime("%Y-%m-%d %H:%M"),
            val_header: m.value,
            cat_header: i18n.get_translation(f"categories.{m.category.value}", lang),
            notes_header: m.notes or ""
        })
        
    df = pd.DataFrame(data)
    
    if not os.path.exists("temp"):
        os.makedirs("temp")
    file_path = f"temp/diabetes_report_{user.id}.xlsx"
    
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Measurements")
    
    return FileResponse(
        path=file_path,
        filename=f"diyabet_raporu_{datetime.now().strftime('%Y%m%d')}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=None
    )
