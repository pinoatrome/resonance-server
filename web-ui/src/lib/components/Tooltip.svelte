<script lang="ts">
	let {tip, children, tipClass="text-text", placement='right', ray=5} = $props();

	let isVisible = $state<boolean>(false);

	function mouseOver() {
		isVisible = true;
	}

	function mouseLeave() {
		isVisible = false;
	}

	let placementClasses = $state<string>()

	$effect(() => {
		if (placement === 'top') {
			placementClasses = '-top-10 -left-10';
        } else if (placement === 'right') {
			placementClasses = `-top-1 left-0 ml-${ray}`;
        } else if (placement === 'bottom') {
			placementClasses = 'top-10 -left-10';
        } else if (placement === 'left') {
			placementClasses = '-top-1 right-0 mr-5';
        }
    });

	const uniqueID = Math.floor(Math.random() * 100);
</script>

<div
     role="tooltip"
     aria-labelledby={`tooltip-${uniqueID}`}
     onblur={mouseLeave}
     onfocus={mouseOver}
     onmouseleave={mouseLeave}
     onmouseover={mouseOver}
>
    <span class="relative">
{#if isVisible}
        <span class="{placementClasses} z-500 p-2 rounded-sm border shadow-xl border-border bg-surface-0 text-xs absolute overflow-auto whitespace-nowrap">
            <span class={tipClass}>{tip}</span>
        </span>
{/if}
    </span>
    {@render children?.()}
</div>

<style>
</style>
