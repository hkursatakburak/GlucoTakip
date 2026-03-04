"""
Admin Panel Router — /admin
Tüm endpoint'ler require_admin dependency ile korunur.
"""
import io
import csv
import pandas as pd

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import crud, database
from routers.auth import get_current_user_from_cookie

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")


# ── Auth Guard ────────────────────────────────────────────────────────────────

def require_admin(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login?next=/admin"},
        )
    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu sayfaya erişim yetkiniz yok.",
        )
    return user


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    stats = crud.get_dashboard_stats(db)
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "admin": admin, **stats},
    )


# ── Kullanıcı Listesi ──────────────────────────────────────────────────────────

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    users = crud.get_all_users(db)
    return templates.TemplateResponse(
        "admin_users.html",
        {"request": request, "admin": admin, "users": users},
    )


# ── Kullanıcı Detay ───────────────────────────────────────────────────────────

@router.get("/users/{user_id}", response_class=HTMLResponse)
async def admin_user_detail(
    user_id: str,
    request: Request,
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    user, measurements = crud.get_user_with_measurements(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return templates.TemplateResponse(
        "admin_user_detail.html",
        {
            "request": request,
            "admin": admin,
            "target_user": user,
            "measurements": measurements,
        },
    )


# ── Şifre Zorla Değiştir ──────────────────────────────────────────────────────

@router.post("/users/{user_id}/set-password")
async def admin_set_password(
    user_id: str,
    new_password: str = Form(...),
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Şifre en az 6 karakter olmalıdır.")
    success = crud.admin_force_set_password(db, user_id, new_password)
    if not success:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return RedirectResponse(
        url=f"/admin/users/{user_id}?msg=Şifre+başarıyla+güncellendi",
        status_code=status.HTTP_302_FOUND,
    )


# ── Admin Rolü Aç/Kapat ───────────────────────────────────────────────────────

@router.post("/users/{user_id}/toggle-admin")
async def admin_toggle_admin(
    user_id: str,
    request: Request,
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    # Kendini adminlikten çıkarmayı önle
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Kendi admin rolünüzü değiştiremezsiniz.")
    user = crud.admin_toggle_admin(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


# ── Kullanıcı Sil ─────────────────────────────────────────────────────────────

@router.post("/users/{user_id}/delete")
async def admin_delete_user(
    user_id: str,
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Kendi hesabınızı silemezsiniz.")
    success = crud.admin_delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


# ── AI Dataset Export: CSV ────────────────────────────────────────────────────

@router.get("/export/csv")
async def export_csv(
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    rows = crud.get_all_measurements_anonymous(db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "value", "category", "measured_at", "notes"])
    for r in rows:
        writer.writerow([r.id, r.user_id, r.value, r.category, r.measured_at, r.notes])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=glucotakip_dataset.csv"},
    )


# ── AI Dataset Export: Excel ──────────────────────────────────────────────────

@router.get("/export/excel")
async def export_excel(
    db: Session = Depends(database.get_db),
    admin=Depends(require_admin),
):
    rows = crud.get_all_measurements_anonymous(db)

    data = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "value": r.value,
            "category": str(r.category),
            "measured_at": r.measured_at,
            "notes": r.notes,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Measurements")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=glucotakip_dataset.xlsx"},
    )
