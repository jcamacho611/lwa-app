# LWA / IWA

Monorepo for the LWA / IWA project.

## Repo Layout

```text
LWA/
├── README.md
├── docs/
├── lwa-backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── runtime.txt
│   └── app/
├── lwa-web/
│   ├── README.md
│   ├── package.json
│   └── app/
└── lwa-ios/
    ├── README.md
    ├── LWA.xcodeproj/
    └── LWA/
```

## Railway Deploy

### Backend Service

- Root Directory = `lwa-backend/`
- Start Command = `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `lwa-ios/` is not a Railway deployment target

### Frontend Service

- Root Directory = `lwa-web/`
- Build Command = `npm install && npm run build`
- Start Command = `npm run start`
- Environment Variable = `NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app`

`lwa-web/` is a standalone browser frontend and can be linked from Whop, your own domain, Gumroad, Lemon Squeezy, and any other URL-based flow.

## Backend Notes

The Railway service should deploy only the FastAPI backend from `lwa-backend/`.

Required backend endpoints:

- `GET /`
- `GET /health`
- `POST /generate`
- `POST /process`
- `POST /v1/jobs`

Local backend run:

```bash
cd lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## iOS Notes

`lwa-ios/` is for Xcode, Simulator, and device builds only.

Do not point Railway at `lwa-ios/`.
