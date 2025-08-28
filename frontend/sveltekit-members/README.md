SvelteKit Members UI (Beta)

Quick start

1) Install Node.js 18+ and pnpm or npm
2) From this folder:
   - pnpm install   (or: npm install)
   - pnpm dev       (or: npm run dev)

Dev server runs on http://localhost:5173

The app fetches members from Django at:
  GET http://localhost:8000/people/members/api/

Authentication: relies on Django session. Ensure you are logged in at
http://localhost:8000/accounts/login/ in the same browser.

Build (static)
  - pnpm build  (or: npm run build)
  The static site will be generated into build/ using adapter-static.

