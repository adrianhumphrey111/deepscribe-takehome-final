# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid Next.js + Flask application that uses Next.js (v13.4.3) as the frontend and Flask (v3.0.3) as the Python API backend. The Flask API is mapped to `/api/*` routes through Next.js rewrites.

## Key Commands

**Development:**
```bash
pnpm dev          # Run both Next.js and Flask concurrently (main dev command)
pnpm next-dev     # Run only Next.js frontend
pnpm flask-dev    # Run only Flask backend (port 5328)
```

**Build & Production:**
```bash
pnpm build        # Build Next.js for production
pnpm start        # Start Next.js production server
```

**Code Quality:**
```bash
pnpm lint         # Run Next.js ESLint
```

## Architecture

**Frontend (Next.js):**
- `/app` - Next.js 13 app directory with TypeScript
- Uses Tailwind CSS with shadcn/ui component library setup
- Path alias `@/*` maps to the project root

**Backend (Flask):**
- `/api` - Flask API directory
- `/api/index.py` - Main Flask application entry point
- API routes are accessible at `/api/*` in the Next.js app
- Runs on port 5328 in development

**API Integration:**
- `next.config.js` rewrites `/api/*` requests to Flask backend
- In development: rewrites to `http://127.0.0.1:5328`
- In production: deployed as Vercel serverless functions

## Important Notes

- No testing framework is currently configured
- TypeScript strict mode is enabled
- Uses pnpm as the package manager (evident from pnpm-lock.yaml)
- Configured for Vercel deployment with Python serverless functions
- Dark mode support is configured in Tailwind