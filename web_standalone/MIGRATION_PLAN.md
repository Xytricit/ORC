# ORC Web App - Next.js Migration Plan

## Goal
Migrate the Flask web app to Next.js for Vercel deployment while maintaining the exact same look and functionality.

## Tech Stack
- **Framework:** Next.js 14 (App Router)
- **Auth:** NextAuth.js
- **Styling:** CSS Modules (port existing CSS)
- **Database:** Vercel KV (key-value store for user sessions)
- **Language:** TypeScript (for better type safety)

## Pages to Build
1. Landing page (`/`)
2. Sign in page (`/auth/signin`)
3. Sign up page (`/auth/signup`)
4. Dashboard (`/dashboard`)

## Features to Implement
- ✅ User authentication (sign up, sign in, sign out)
- ✅ Protected routes (dashboard requires login)
- ✅ Session management
- ✅ Same UI/UX as Flask version
- ✅ Responsive design
- ✅ Black/green color scheme

## File Structure
```
web_standalone/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   ├── auth/
│   │   ├── signin/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   └── api/
│       └── auth/
│           └── [...nextauth]/
│               └── route.ts
├── components/
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   └── ...
├── styles/
│   ├── globals.css
│   ├── landing.module.css
│   ├── auth.module.css
│   └── dashboard.module.css
├── lib/
│   └── auth.ts
├── public/
│   └── images/
├── package.json
├── tsconfig.json
└── next.config.js
```

## Implementation Steps
1. Initialize Next.js project
2. Set up TypeScript configuration
3. Port CSS files to CSS Modules
4. Copy images and static assets
5. Build landing page component
6. Build auth pages (signin/signup)
7. Set up NextAuth.js
8. Build protected dashboard
9. Configure Vercel deployment
10. Test and deploy

## Database Schema (Vercel KV)
```
users:{userId} = {
  id: string,
  username: string,
  email: string,
  passwordHash: string,
  createdAt: timestamp
}

sessions:{sessionId} = {
  userId: string,
  expiresAt: timestamp
}
```

## Environment Variables
- `NEXTAUTH_SECRET`: Random secret for NextAuth
- `NEXTAUTH_URL`: Production URL
- `KV_REST_API_URL`: Vercel KV URL (auto-provided)
- `KV_REST_API_TOKEN`: Vercel KV token (auto-provided)
