from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import io
import crud, database
from routers.auth import get_current_user_from_cookie
import pandas as pd
import i18n
import logging

logger = logging.getLogger(__name__)

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

    end_date = datetime.now()
    if date_range == "7":
        start_date = end_date - timedelta(days=7)
    elif date_range == "30":
        start_date = end_date - timedelta(days=30)
    elif date_range == "90":
        start_date = end_date - timedelta(days=90)
    else:
        # "all" — go back 20 years
        start_date = end_date - timedelta(days=7300)

    # Fetch and convert to list immediately — avoids SQLAlchemy lazy-iteration issues
    measurements = list(crud.get_measurements_by_date_range(db, user.id, start_date, end_date))
    logger.info(f"[EXPORT] user={user.id} range={date_range} rows={len(measurements)}")

    # Failsafe: if date range returned 0 rows, return ALL measurements instead
    if len(measurements) == 0:
        logger.warning(f"[EXPORT] Date-range returned 0 rows — falling back to ALL for user {user.id}")
        measurements = list(crud.get_measurements(db, user_id=user.id, limit=10000))
        logger.info(f"[EXPORT] Fallback fetched {len(measurements)} rows")

    lang = i18n.get_language(request)

    val_header   = i18n.get_translation("admin.table_value", lang)
    cat_header   = i18n.get_translation("admin.table_category", lang)
    date_header  = i18n.get_translation("admin.table_date", lang)
    notes_header = i18n.get_translation("add_measurement.notes_label", lang)

    data = []
    for m in measurements:
        data.append({
            date_header:  m.measured_at.strftime("%Y-%m-%d %H:%M"),
            val_header:   m.value,
            cat_header:   i18n.get_translation(f"categories.{m.category.value}", lang),
            notes_header: m.notes or ""
        })

    logger.info(f"[EXPORT] DataFrame rows: {len(data)}")
    df = pd.DataFrame(data)

    # Write to in-memory buffer — no temp files on Render's ephemeral filesystem
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Measurements")
    # seek MUST be outside the 'with' block — openpyxl finalizes on __exit__
    output.seek(0)

    filename = f"GlucoTakip_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
