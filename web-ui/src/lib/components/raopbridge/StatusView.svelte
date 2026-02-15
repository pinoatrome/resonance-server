<script lang="ts">
	let { info } = $props();
</script>
{#if !!info }
<div class="flex flex-col items-start justify-end text-overlay-0">
      <div class="text-lg">{info.name} v.{info.version}</div>
      <div class="text-xs">{info.description}</div>
</div>
{/if}
