<script lang="ts">
	import { type PluginStatus } from '$lib/components/raopbridge/raopbridgeApi';
	import {
		ActivityIcon,
		ShieldQuestionIcon,
		TriangleAlertIcon,
		BadgeInfo
	} from 'lucide-svelte';
	import { toastStore } from '$lib/stores/toast.svelte';
	import ModalDialog from "$lib/components/ModalDialog.svelte";
	import Switch from "$lib/components/Switch.svelte";
	import Tooltip from "$lib/components/Tooltip.svelte";

	// Props
	let {status, onToggle}: { status: PluginStatus, onToggle: () => Promise<boolean> } = $props();

	let bridgeActive = $derived<boolean>(status.bridge === 'active');
	let toggleCommand = $state<'Activate' | 'Deactivate' | null>(null);
	let isToggleInProgress = $state(false);
	let bridgeStatus = $derived<'active' | 'inactive' | null>(status.bridge);

	async function toggleStatus() { toggleCommand = bridgeStatus === 'active' ? 'Deactivate' : 'Activate'; }

    async function cancelToggleStatus() { toggleCommand = null; }

    async function confirmToggleStatus(): Promise<void> {
		let error : Error | null = null;
		try {
			isToggleInProgress = true;
			const result = await onToggle()
			if (result) {
				toastStore.success(`Command "${toggleCommand}" done`);
			} else {
				toastStore.warning(`Command "${toggleCommand}" failed - check the settings and logs for errors`)
			}
		} catch (err) {
			error = err as Error;
		}
		if (!!error) {
			const msg = `Failed to execute command: "${toggleCommand}"`;
			toastStore.error(msg, { detail: error.message });
		}
		isToggleInProgress = false;
		toggleCommand = null;
	}
</script>

{#if !!toggleCommand}
<ModalDialog
	isOpen={!!toggleCommand}
	inProgress={isToggleInProgress}
	onCancel={cancelToggleStatus}
	onConfirm={confirmToggleStatus}
>
<div class="flex flex-1 items-center justify-center text-lg">
	{#if toggleCommand === 'Activate'}
	<div class="flex">
		<ShieldQuestionIcon class="text-success shrink-0" />
		<div class="ml-3">Confirm Plugin Activation?</div>
	</div>
	{:else}
	<div class="flex flex-col gap-3">
		<div class="flex flex-row justify-center">
			<TriangleAlertIcon class="text-error shrink-0" />
			<div class="ml-3">Confirm Plugin Deactivation?</div>
		</div>
		<div class="text-sm">This will stop all active players managed via the plugin.</div>
	</div>
	{/if}
</div>
</ModalDialog>
{/if}
{#if status?.plugin === 'enabled'}
<div class="flex flex-1">
	<div class="p-3">
	{#if bridgeStatus === 'active'}
	<Tooltip tip="The bridge is active: disable it to edit the values" ray={10}>
		<ActivityIcon class="text-success px-0 mx-2"/>
	</Tooltip>
	{:else}
	<Tooltip tip="The bridge is disabled: edit the values and activate it" ray={10}>
		<BadgeInfo class="text-muted px-0 mx-2"/>
	</Tooltip>

	{/if}
	</div>
	<div class="mt-1 ml-auto mr-3">
		<Switch options={['Disabled', 'Active']}
				classes="border px-4 py-2 mt-2 mb-0 mr-2 rounded-lg bg-surface-1 hover:bg-surface-0 text-lg text-overlay-1 hover:text-accent-hover transition-colors"
				showValue={true}
				bind:value={bridgeActive}
				onToggle={toggleStatus}
				disabled={!bridgeStatus || isToggleInProgress}
		/>
    </div>
	</div>
{/if}

