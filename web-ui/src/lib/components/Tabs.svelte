<script lang="ts">
	let {active, pages, onchange} : {pages: string[], active: number, onchange: (idx: number) => void} = $props();
	let activePage = $derived<number>(active);
</script>

<div class="flex tab-container">
    {#each pages as page, idx}
        <button class="tab" class:active={activePage===idx} onclick={() => {onchange(idx)}}>{page}</button>
    {/each}
    <div class="tab-filler"></div>
</div>

<style>

    .tab-filler {
        flex-grow: 1;
        border-bottom: 1px solid var(--color-border);
    }

    .tab-container {
        color: inherit;
    }

	.tab {
        color: var(--color-muted);
		background-color: var(--color-surface-0);
		float: left;
		outline: none;
        border: 1px solid var(--color-border);
		border-radius: 10px 10px 0 0;
		cursor: pointer;
		padding: 5px 10px;
		width: 20%;
        &.active {
            border-bottom: 0;
            cursor: inherit;
            color: var(--color-accent);
            background-color: inherit;
        }
	}

	.tab:hover {
        color: var(--color-accent-hover);
        background-color: var(--color-surface-1);
        &.active {
            cursor: inherit;
            color: var(--color-accent);
            background-color: inherit;
        }
	}

</style>
