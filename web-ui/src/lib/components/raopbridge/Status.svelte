<script lang="ts">
    // Props
	let { info, status }: { info: any; status: any } = $props();
</script>
{#if !!info }
      <section>{info.name} v.{info.version}
      {#if !!status }
        ({status.plugin==='running' ? status.bridge : 'Inactive'})
      {/if}
      </section>
{/if}
