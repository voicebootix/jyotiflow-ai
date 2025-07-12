import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Import and initialize Sentry
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "https://f758f026f026fecdad12bef7f620e18d4509655670f086364.ingest.us.sentry.io/4506956586319216",
  tracesSampleRate: 1.0,
});

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
