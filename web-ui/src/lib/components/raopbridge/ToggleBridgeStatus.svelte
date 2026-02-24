<script lang="ts">
    // Props
    let { status }: { status: any } = $props();
    function toggleStatus() {
		console.log('toggle bridge status: ' + status?.plugin);
	}
</script>
{#if status?.plugin==='running'}
      <section> <button
        class="p-2 rounded-lg hover:bg-surface-1 text-overlay-1 hover:text-error transition-colors"
        onclick="{toggleStatus}"
        disabled="{!status?.bridge}"
      >{status?.bridge === 'active' ? 'Deactivate' : 'Activate'}</button>
      </section>
{/if}

