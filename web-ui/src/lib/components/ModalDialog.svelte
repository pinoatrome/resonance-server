<script lang="ts">
	import {Loader2Icon, X} from 'lucide-svelte';

	// Props
	let {
		onConfirm,
		onCancel,
		isOpen = false,
        inProgress = false,
		title = 'Confirm',
        headerLine = true,
        hideCancel = false,
        labelOK = 'OK',
        labelCancel = 'Cancel',
		children
	}: {
		onConfirm: () => void,
		onCancel: () => void,
		isOpen: boolean,
		inProgress?: boolean | null,
		title?: string,
        headerLine?: boolean,
        hideCancel?: boolean
        labelOK?: string,
        labelCancel?: string,
		children?: any
	} = $props();

	function handleOk() {
		onConfirm();
	}

	function handleClose() {
		onCancel();
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			handleClose();
		}
	}
</script>

{#if isOpen}
    <!-- Backdrop -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
            class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center p-4"
            onkeydown={handleKeydown}
            onclick={handleClose}
    >
        <!-- Modal -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <div
                class="bg-base rounded-2xl shadow-2xl w-full max-w-lg border border-surface-1 overflow-hidden"
                onclick={(e) => e.stopPropagation()}
        >
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 {headerLine ? 'border-b' : ''} border-surface-1">
                <div class="flex">
                    {title}
                </div>
                <button
                        class="p-2 rounded-lg hover:bg-surface-0 text-overlay-1 hover:text-text transition-colors"
                        onclick={handleClose}
                        aria-label="Close"
                >
                    <X size={20}/>
                </button>
            </div>

            <!-- Content -->
            <div class="p-6 space-y-4">
                {#if !!children}
                    {@render children()}
                {/if}
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-surface-1 bg-mantle">
                {#if !hideCancel}
                    <button
                        class="px-4 py-2 rounded-xl hover:bg-surface-0 text-overlay-1 hover:text-text
                       font-medium transition-colors"
                        onclick={handleClose}
                >
                    {labelCancel}
                </button>
                {/if}
                <button class="px-4 py-2 rounded-xl hover:bg-surface-0 text-overlay-1 hover:text-text font-medium transition-colors"
                        onclick={handleOk}
                        disabled={inProgress}
                >
                    {#if inProgress}<Loader2Icon class="animate-spin inline"/>{:else}{labelOK}{/if}
                </button>
            </div>
        </div>
    </div>
{/if}
