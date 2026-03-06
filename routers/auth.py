from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
import crud, schemas, database, auth
import os
from authlib.integrations.starlette_client import OAuth
from email_utils import send_email, build_verification_email, build_password_reset_email

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="templates")
import i18n
i18n.setup_templates(templates)

oauth = OAuth()

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={
        'scope': 'openid email profile'
    }
)

oauth.register(
    name='apple',
    server_metadata_url='https://appleid.apple.com/.well-known/openid-configuration',
    client_id=os.getenv("APPLE_CLIENT_ID"),
    client_secret=os.getenv("APPLE_PRIVATE_KEY"),
    client_kwargs={
        'scope': 'name email'
    }
)

def get_current_user_from_cookie(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except auth.JWTError:
        return None
    user = crud.get_user_by_email(db, email=email)
    return user

@router.get("/auth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    if provider == "google":
        redirect_uri = os.getenv("REDIRECT_URI")
        if not redirect_uri:
            redirect_uri = str(request.url_for("auth_callback", provider="google"))
        return await oauth.google.authorize_redirect(request, redirect_uri)
    elif provider == "apple":
        redirect_uri = str(request.url_for("auth_callback", provider="apple"))
        return await oauth.apple.authorize_redirect(request, redirect_uri)
    return RedirectResponse(url="/login")

@router.get("/auth/{provider}/callback")
async def auth_callback(provider: str, request: Request, db: Session = Depends(database.get_db)):
    try:
        if provider == "google":
            token = await oauth.google.authorize_access_token(request)
            user_info = token.get("userinfo")
            if not user_info:
                return RedirectResponse(url="/login?error=Google+login+failed")
            email = user_info.get("email")
            full_name = user_info.get("name", "Google Kullanıcısı")
            
        elif provider == "apple":
            token = await oauth.apple.authorize_access_token(request)
            user_info = token.get("userinfo")
            if not user_info:
                return RedirectResponse(url="/login?error=Apple+login+failed")
            email = user_info.get("email")
            full_name = user_info.get("name", "Apple Kullanıcısı")
        else:
            return RedirectResponse(url="/login")

        if not email:
            return RedirectResponse(url="/login?error=Email+not+provided+by+identity+provider")

        # Get or create user implicitly handling oauth flow
        user = crud.get_or_create_oauth_user(db, email=email, full_name=full_name)

        # For SSO logins, automatically apply "Remember Me" (e.g. 30 days)
        access_token_expires = timedelta(days=30)
        access_token = auth.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=30 * 24 * 60 * 60,
            expires=30 * 24 * 60 * 60,
        )
        return response
    except Exception as e:
        print(f"SSO ERROR: {e}") # ADDED FOR DEBUGGING
        return RedirectResponse(url=f"/login?error=SSO+Error")

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    data_consent: bool = Form(False),
    db: Session = Depends(database.get_db)
):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Bu e-posta adresi zaten kullanımda."
        })
    user_schema = schemas.UserCreate(
        email=email,
        full_name=full_name,
        password=password,
        data_consent=data_consent
    )
    crud.create_user(db=db, user=user_schema)
    
    token = auth.create_email_token(email=email, token_type="verify_email")
    verify_url = str(request.url_for("verify_email")) + f"?token={token}"
    email_body = build_verification_email(full_name=full_name, verify_url=verify_url)
    background_tasks.add_task(send_email, email, "GlucoTakip Hesabınızı Doğrulayın", email_body)
    
    return RedirectResponse(url="/login?registered=true", status_code=status.HTTP_302_FOUND)

@router.get("/auth/verify-email", name="verify_email")
async def verify_email(request: Request, token: str, db: Session = Depends(database.get_db)):
    email = auth.verify_email_token(token, "verify_email")
    if not email:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Geçersiz veya süresi dolmuş doğrulama bağlantısı."})
    
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Kullanıcı bulunamadı."})
    
    user.is_verified = True
    db.commit()
    return RedirectResponse(url="/login?verified=true", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, registered: str = None, verified: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "registered": registered, "verified": verified})

@router.get("/apple-soon", response_class=HTMLResponse)
async def apple_soon_page(request: Request):
    return templates.TemplateResponse("apple_coming_soon.html", {"request": request})

@router.post("/login")
async def login(
    response: Response,
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember_me: str = Form(None),
    db: Session = Depends(database.get_db)
):
    user = crud.get_user_by_email(db, email=email)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Geçersiz e-posta veya şifre"
        })
        
    if not getattr(user, "is_verified", True):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Lütfen giriş yapmadan önce e-posta adresinizi doğrulayın."
        })
    
    if remember_me == "on":
        # Keep user logged in for 30 days
        expiry_days = 30
        access_token_expires = timedelta(days=expiry_days)
        max_age = expiry_days * 24 * 60 * 60
    else:
        # Session cookie, or very short-lived
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        max_age = None # Browser will delete when closed

    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    cookie_kwargs = {
        "key": "access_token",
        "value": f"Bearer {access_token}",
        "httponly": True,
    }
    
    if max_age is not None:
        cookie_kwargs["max_age"] = max_age
        cookie_kwargs["expires"] = max_age

    response.set_cookie(**cookie_kwargs)
    return response

@router.get("/auth/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/auth/forgot-password")
async def forgot_password(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "error": "Bu e-posta adresi sistemimizde kayıtlı değil. Lütfen kontrol edip tekrar deneyin."
        })

    # ── Doğrulanmamış hesap kontrolü ──────────────────────────────────────────
    if not getattr(user, "is_verified", True):
        # Şifre sıfırlama GÖNDERILMEZ; yeni aktivasyon maili fırlatılır
        verify_token = auth.create_email_token(email=email, token_type="verify_email")
        verify_url = str(request.url_for("verify_email")) + f"?token={verify_token}"
        activation_body = build_verification_email(full_name=user.full_name, verify_url=verify_url)
        background_tasks.add_task(
            send_email, email, "GlucoTakip Hesabınızı Doğrulayın", activation_body
        )
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "warning": "Mail adresiniz onaylanmadı. Aktivasyon maili tekrar gönderildi."
        })

    token = auth.create_email_token(email=email, token_type="reset_password")
    reset_url = str(request.url_for("reset_password_page")) + f"?token={token}"
    email_body = build_password_reset_email(full_name=user.full_name, reset_url=reset_url)
    background_tasks.add_task(send_email, email, "GlucoTakip Şifre Sıfırlama", email_body)

    return templates.TemplateResponse("message_page.html", {
        "request": request, 
        "title": "Şifre Sıfırlama Bağlantısı Gönderildi",
        "message": "Şifre sıfırlama bağlantısı e-posta adresinize gönderilmiştir."
    })

@router.get("/auth/reset-password", response_class=HTMLResponse, name="reset_password_page")
async def reset_password_page(request: Request, token: str):
    email = auth.verify_email_token(token, "reset_password")
    if not email:
        return templates.TemplateResponse("message_page.html", {
            "request": request,
            "title": "Geçersiz Bağlantı",
            "message": "Şifre sıfırlama bağlantısı geçersiz veya süresi dolmuş."
        })
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

@router.post("/auth/reset-password")
async def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(database.get_db)
):
    email = auth.verify_email_token(token, "reset_password")
    if not email:
        return templates.TemplateResponse("message_page.html", {
            "request": request,
            "title": "Geçersiz Bağlantı",
            "message": "Şifre sıfırlama bağlantısı geçersiz veya süresi dolmuş."
        })
    
    if password != password_confirm:
        return templates.TemplateResponse("reset_password.html", {
            "request": request, 
            "token": token,
            "error": "Şifreler eşleşmiyor."
        })
        
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return templates.TemplateResponse("message_page.html", {
            "request": request,
            "title": "Hata",
            "message": "Kullanıcı bulunamadı."
        })
        
    user.hashed_password = auth.get_password_hash(password)
    db.commit()
    
    return templates.TemplateResponse("message_page.html", {
        "request": request,
        "title": "Şifre Sıfırlandı",
        "message": "Şifreniz başarıyla güncellendi. Artık yeni şifrenizle giriş yapabilirsiniz."
    })

@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
