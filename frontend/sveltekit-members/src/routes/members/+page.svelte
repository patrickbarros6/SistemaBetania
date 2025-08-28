<script>
  import { onMount } from 'svelte';

  let q = '';
  let loading = true;
  let error = '';
  let items = [];

  async function load() {
    loading = true; error = '';
    try {
      const url = new URL('http://localhost:8000/people/members/api/');
      if (q) url.searchParams.set('q', q);
      const res = await fetch(url, { credentials: 'include' });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      items = data.results || [];
    } catch (e) {
      error = 'Falha ao carregar. Verifique login no Django e CORS.';
    } finally {
      loading = false;
    }
  }

  onMount(load);
</script>

<section>
  <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:1rem;">
    <div>
      <div style="font-size:.75rem; color:#666">Pessoas /</div>
      <h1 style="margin:.25rem 0; font-size:1.75rem; font-weight:600;">Membros</h1>
      <p style="color:#666; max-width:56ch">Lista consumindo /people/members/api/ com sessão do Django.</p>
    </div>
    <div>
      <button on:click={() => alert('Novo membro (placeholder)')} style="padding:.5rem .75rem; background:#111; color:#fff; border-radius:.5rem;">+ Novo membro</button>
    </div>
  </div>

  <div style="margin-top:1rem; display:flex; gap:.5rem;">
    <input bind:value={q} placeholder="Buscar por nome" style="border:1px solid #d0d4d9; padding:.5rem .75rem; border-radius:.5rem; min-width:280px"/>
    <button on:click={load} style="padding:.5rem .75rem; border:1px solid #d0d4d9; border-radius:.5rem; background:#fff">Buscar</button>
  </div>

  {#if loading}
    <p style="margin-top:1rem; color:#666">Carregando...</p>
  {:else if error}
    <p style="margin-top:1rem; color:#c00">{error}</p>
  {:else}
    {#if items.length === 0}
      <div style="margin-top:2rem; text-align:center; color:#666">Nenhum membro encontrado.</div>
    {:else}
      <div style="margin-top:1rem; overflow:auto;">
        <table style="width:100%; border-collapse:collapse;">
          <thead>
            <tr style="text-align:left; color:#666;">
              <th style="padding:.5rem .5rem;">Nome</th>
              <th style="padding:.5rem .5rem;">Telefone</th>
              <th style="padding:.5rem .5rem;">Elegível</th>
              <th style="padding:.5rem .5rem;">Status</th>
            </tr>
          </thead>
          <tbody>
            {#each items as m}
              <tr>
                <td style="padding:.5rem .5rem; border-top:1px solid #eee;">{m.name}</td>
                <td style="padding:.5rem .5rem; border-top:1px solid #eee;">{m.phone || '—'}</td>
                <td style="padding:.5rem .5rem; border-top:1px solid #eee;">{m.kitchen_eligible ? 'Sim' : 'Não'}</td>
                <td style="padding:.5rem .5rem; border-top:1px solid #eee;">{m.active ? 'Ativo' : 'Inativo'}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  {/if}
</section>

