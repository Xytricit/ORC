# ORC Web App - Next.js

Modern, serverless-ready web application for ORC (Optimization & Refactoring Catalyst).

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** CSS Modules
- **Authentication:** Custom session-based auth
- **Deployment:** Vercel

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Deployment to Vercel

1. Push this code to GitHub
2. Import the project in Vercel
3. Set Root Directory to `web_standalone`
4. Add environment variable:
   - `SESSION_SECRET`: A random secret string
5. Deploy!

## Features

- ✅ Landing page
- ✅ User authentication (Sign up / Sign in)
- ✅ Protected dashboard
- ✅ Session management
- ✅ Responsive design
- ✅ Modern UI with black/green theme

## Project Structure

```
web_standalone/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   ├── auth/              # Auth pages
│   ├── dashboard/         # Dashboard page
│   └── api/               # API routes
├── lib/                   # Utility functions
├── styles/                # CSS modules
├── public/                # Static assets
└── package.json
```
