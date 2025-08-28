<script>
  export let data;
</script>

<svelte:head>
  <title>Betânia · Members</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
</svelte:head>

<div style="font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#f6f7f9; min-height:100vh;">
  <nav style="background:#111; color:#fff; padding:.75rem 1rem; display:flex; gap:1rem; align-items:center;">
    <a href="/" style="color:#fff; font-weight:700; text-decoration:none;">BETÂNIA</a>
    <a href="/members" style="color:#fff; text-decoration:none; opacity:.9;">Membros</a>
  </nav>
  <main style="max-width:1120px; margin: 1.25rem auto; padding: 0 1rem;">
    <slot />
  </main>
</div>

