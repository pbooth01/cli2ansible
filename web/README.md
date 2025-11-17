# cli2ansible Web UI

Modern Next.js web interface for the cli2ansible application.

## Features

- ⚡ Built with Next.js 14 and React 18
- 🎨 Styled with Tailwind CSS
- 📱 Fully responsive design
- 🔄 Real-time API integration
- ✨ Beautiful UI components with Lucide icons

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000 in your browser
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Docker

Build and run with Docker:

```bash
docker build -t cli2ansible-web .
docker run -p 3000:3000 cli2ansible-web
```

Or use Docker Compose from the root directory:

```bash
docker-compose up web
```

## Project Structure

```
web/
├── app/                 # Next.js app directory
│   ├── page.tsx        # Home page
│   ├── layout.tsx      # Root layout
│   ├── globals.css     # Global styles
│   ├── create/         # Create session page
│   └── sessions/       # Sessions pages
├── components/         # Reusable React components
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Header.tsx
│   ├── Input.tsx
│   └── Status.tsx
├── lib/               # Utilities and API client
│   └── api.ts        # API client
├── public/           # Static assets
└── package.json      # Dependencies
```

## Pages

- `/` - Home page with introduction
- `/sessions` - List all sessions
- `/create` - Create new session
- `/sessions/[id]` - Session details and compilation

## API Integration

The app communicates with the FastAPI backend at `http://localhost:8000`.

Key API endpoints:
- `POST /sessions` - Create session
- `GET /sessions/{id}` - Get session details
- `POST /sessions/{id}/compile` - Compile session
- `GET /sessions/{id}/report` - Get compilation report
- `POST /sessions/{id}/cast` - Upload .cast file

See [lib/api.ts](lib/api.ts) for complete API client implementation.

## Styling

Tailwind CSS is configured with:
- Custom color schemes
- Responsive design utilities
- Dark mode support ready

See [tailwind.config.js](tailwind.config.js) for configuration.

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `/api`)

## Testing

Currently no tests configured. To add tests:

```bash
npm install --save-dev jest @testing-library/react
```

## Contributing

Follow the existing code style and component patterns. Use TypeScript for type safety.

## License

Same as parent project
