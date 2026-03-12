# AGENTS.md - Frontend

This file provides guidance for AI agents working on the cli2ansible frontend.

## What This Component Does

The frontend is a Next.js 14 web application that provides a user interface for:

1. **Creating** new terminal recording sessions
2. **Uploading** asciinema .cast files
3. **Viewing** session details and extracted commands
4. **Triggering** Ansible playbook compilation
5. **Downloading** generated Ansible roles

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Linting**: ESLint with Next.js config

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx            # Home page
│   ├── layout.tsx          # Root layout
│   ├── globals.css         # Global styles
│   ├── create/             # Create session page
│   │   └── page.tsx
│   └── sessions/           # Session pages
│       ├── page.tsx        # Sessions list
│       └── [id]/           # Session details
│           └── page.tsx
├── components/             # Reusable UI components
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Header.tsx
│   ├── Input.tsx
│   └── Status.tsx
├── lib/                    # Utilities
│   └── api.ts              # API client
├── public/                 # Static assets
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
└── tsconfig.json           # TypeScript configuration
```

## Running Tests

**Note**: The frontend does not currently have tests configured.

To add tests, install testing dependencies:

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

Then create test files with `.test.tsx` or `.spec.tsx` extensions.

## Development Commands

```bash
# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Docker

```bash
# Build Docker image
docker build -t cli2ansible-web .

# Run container
docker run -p 3000:3000 cli2ansible-web

# Or use docker-compose from project root
docker-compose up web
```

## API Integration

The frontend communicates with the FastAPI backend. API client is in `lib/api.ts`.

**Key Endpoints** (prefixed with `/api/v1`):
- `POST /sessions` - Create session
- `GET /sessions/{id}` - Get session details
- `POST /sessions/{id}/cast` - Upload .cast file
- `POST /sessions/{id}/compile` - Compile to Ansible
- `GET /sessions/{id}/report` - Get compilation report

**Environment Variables**:
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `/api/v1`)

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home page with introduction |
| `/sessions` | List all sessions |
| `/create` | Create new session form |
| `/sessions/[id]` | Session details and compilation |

## Styling Guidelines

- Use Tailwind CSS utility classes
- Follow existing component patterns
- Keep components small and reusable
- Use TypeScript for type safety

