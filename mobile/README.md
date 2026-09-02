# SkinCare AI - React Native Mobile App

## Setup

### Backend
```bash
cd ..
pip install -r requirements.txt
pip install -r backend/requirements.txt
python -m backend.run
```

The backend runs at `http://localhost:8000`.

### Mobile App
```bash
cd mobile
npm install
npx expo start
```

## Environment Variables

Create a `.env` file in the `mobile/` directory:

```
EXPO_PUBLIC_API_URL=http://localhost:8000
```

For Android emulator, use `http://10.0.2.2:8000` instead.
For iOS simulator, `http://localhost:8000` works.

## Project Structure

```
mobile/
├── app/                    # Expo Router (file-based routing)
│   ├── (tabs)/             # Bottom tab navigator
│   │   ├── _layout.tsx     # Tab layout
│   │   ├── index.tsx       # Home/Scan screen
│   │   ├── catalog.tsx     # Product catalog
│   │   ├── history.tsx     # Scan history
│   │   └── settings.tsx    # Settings
│   ├── analysis/
│   │   └── [id].tsx        # Analysis results
│   ├── product/
│   │   └── [id].tsx        # Product detail
│   ├── condition/
│   │   └── [name].tsx      # Condition info
│   └── _layout.tsx         # Root layout
├── components/             # Reusable UI components
├── constants/              # Theme, colors, config
├── hooks/                  # Custom React hooks
├── services/               # API client
├── types/                  # TypeScript interfaces
└── utils/                  # Storage, formatting helpers
```
