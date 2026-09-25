/**
 * main.jsx
 * --------
 * This is the JavaScript entry point for the React app.
 *
 * It does ONE thing: mounts the React application into the HTML page.
 *
 * The HTML page (index.html) has a <div id="root"></div>.
 * React takes over that div and renders our entire <App /> component tree inside it.
 *
 * StrictMode is a development helper — it intentionally renders components
 * twice to help catch bugs early. It has no effect in production.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'  // Global styles + Tailwind CSS
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
