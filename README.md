# LWA

Starter repository for an iOS app plus local FastAPI backend.

LWA is an AI content repurposer for short-form creators. In this first version, the iOS app accepts a video URL, sends it to a local backend, and shows mock clip results with hooks and captions.

## Project Structure

```text
LWA/
├── README.md
├── .gitignore
├── lwa-backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── mock_data.py
│   │   └── schemas.py
│   ├── .dockerignore
│   ├── Dockerfile
│   └── requirements.txt
└── lwa-ios/
    ├── LWA.xcodeproj/
    └── LWA/
        ├── Assets.xcassets/
        ├── ContentView.swift
        ├── Info.plist
        ├── LWAApp.swift
        ├── Models/
        │   └── ClipResult.swift
        ├── Services/
        │   └── APIClient.swift
        └── ViewModels/
            └── ContentViewModel.swift
```

## What Each Part Does

- `lwa-backend/app/main.py`: FastAPI app with `POST /process` and `GET /health`.
- `lwa-backend/app/schemas.py`: Request and response models.
- `lwa-backend/app/mock_data.py`: Placeholder clip results so the full flow works before real AI is added.
- `lwa-backend/requirements.txt`: Python dependencies.
- `lwa-backend/Dockerfile`: Optional containerized backend run.
- `lwa-ios/LWA/LWAApp.swift`: SwiftUI app entry point.
- `lwa-ios/LWA/ContentView.swift`: Single-screen dark UI with URL input, generate button, and results list.
- `lwa-ios/LWA/Models/ClipResult.swift`: Decodable response models for the app.
- `lwa-ios/LWA/Services/APIClient.swift`: Local network call to `http://127.0.0.1:8000/process`.
- `lwa-ios/LWA/ViewModels/ContentViewModel.swift`: Simple state management for loading, results, and errors.
- `lwa-ios/LWA/Info.plist`: App config, including relaxed transport rules for local HTTP during development.
- `lwa-ios/LWA.xcodeproj`: Xcode project you can open and run in the iOS Simulator.

## Backend: Local Run

From the repository root:

```bash
cd lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will start at:

```text
http://127.0.0.1:8000
```

Useful endpoints:

- `GET /health`
- `POST /process`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/process \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://www.youtube.com/watch?v=example"}'
```

## Backend: Docker Run

From the repository root:

```bash
cd lwa-backend
docker build -t lwa-backend .
docker run --rm -p 8000:8000 lwa-backend
```

## iOS App Run

1. Open the project:

```bash
open lwa-ios/LWA.xcodeproj
```

2. In Xcode, choose the `LWA` scheme.
3. Run the app in an iPhone Simulator.
4. Paste a public video URL and tap `Generate Clips`.

The app is already pointed at:

```text
http://127.0.0.1:8000/process
```

Important note:

- `127.0.0.1` is correct for the local backend flow when using the iOS Simulator on your Mac.
- If you later run the app on a physical iPhone, update `lwa-ios/LWA/Services/APIClient.swift` to use your Mac's local network IP instead of `127.0.0.1`.

## Exact Commands To Run Next

Start the backend first:

```bash
cd /Users/bdm/LWA/lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second Terminal window, open the iOS project:

```bash
cd /Users/bdm/LWA
open lwa-ios/LWA.xcodeproj
```

Then in Xcode:

1. Pick an iPhone Simulator.
2. Press Run.
3. Paste a video URL.
4. Tap `Generate Clips`.
