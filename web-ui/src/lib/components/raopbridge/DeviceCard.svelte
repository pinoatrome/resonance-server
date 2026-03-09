<script lang="ts">
    import type {Device} from "$lib/components/raopbridge/raopbridgeApi";
	import {CirclePowerIcon, PencilIcon, Settings, Trash2Icon} from "lucide-svelte";
	import Tooltip from "$lib/components/Tooltip.svelte";

	let {device, expanded, toggle, rename, remove, setup, update, readonly = false} : {
		device: Device,
        expanded: boolean,
        toggle: () => void,
        rename: (v: string) => Promise<boolean>,
        remove: () => void,
        setup: () => void,
        update: (field: string, value: boolean | string) => void,
        readonly: boolean
	} = $props();

	let deviceEnabled = $derived<boolean>(device.enabled);
	let deviceName = $derived<string>(device.name);
	let editNameInfo = $state<any | null>(null);

    const editDeviceName = () => {
		editNameInfo = {
			restore: device.name,
        }
    }

	async function handleRename(): Promise<void> {
		if (!editNameInfo) {
			return
        }
		if (!deviceName) {
			deviceName = editNameInfo.restore;
			editNameInfo = null;
			return;
        }
		if (deviceName === editNameInfo.restore) {
			editNameInfo = null;
			return;
        }
		const result = await rename(deviceName);
        if (result === true) {
			editNameInfo = null;
        }
    }
	const handleRenameKeydown = (event: KeyboardEvent) => {
		if (event.key === 'Escape') {
			editNameInfo = null;
		}
	}
</script>

<button disabled={readonly}
        class="mr-5 {readonly ? 'cursor-not-allowed' : 'cursor-pointer'}"
        onclick={() => update('enabled', !deviceEnabled)}>
    <CirclePowerIcon
        class="inline hover:bg-surface-0 {deviceEnabled ? 'text-success hover:text-accent-hover' : 'text-muted hover:text-hover'}"
    />
</button>
{#if editNameInfo}
<input type="text"
       onchange={handleRename}
       onkeydown={handleRenameKeydown}
       name={`device-name-${device.udn}`}
       placeholder="Name of the player."
       bind:value={deviceName}
       class="text-center flex-1 px-4 py-1 rounded-xl bg-surface-0 border border-surface-1
           placeholder-overlay-0 focus:outline-none focus:ring-2
           focus:ring-accent focus:border-transparent transition-all"
       disabled={readonly}
/>
{:else}
<button class="text-text cursor-pointer" onclick={toggle}>{deviceName}</button>
<button disabled={readonly}
        class="ml-3"
        onclick={editDeviceName}>
    <Tooltip tipClass="text-xs" tip="Rename the device">
        <PencilIcon size={16} class={readonly ? 'text-muted cursor-not-allowed' : 'text-success cursor-pointer'}/>
    </Tooltip>
</button>
    {/if}

{#if expanded}
    <div class="flex flex-col m-5 p-5 gap-y-3 rounded-lg border">
        <div class="flex flex-row">
            <div>UDN:</div>
            <div class="ml-auto">{device.udn}</div>
        </div>
        <div class="flex flex-row">
            <div>Device Name:</div>
            <div class="ml-auto">{device.friendly_name}</div>
        </div>
        <div class="flex flex-row">
            <div>Address:</div>
            <div class="ml-auto">{device.mac}</div>
        </div>
        <div class="flex flex-row">
            <div class="ml-5">
                <Tooltip tipClass="text-xs" tip="Device setup" ray={10} placement="right">
                    <button
                        class="text-text cursor-pointer"
                        onclick={setup}
                    ><Settings class="inline"/></button>
                </Tooltip>
            </div>
            <div class="ml-auto mt-2 mb-0 mr-5">
                <Tooltip tipClass="text-xs" tip={deviceEnabled || readonly ? 'Disable the device first' : 'Remove the device'} placement="top">
                <button disabled={deviceEnabled || readonly}
                        class="{deviceEnabled || readonly ? 'text-muted' : 'text-error'} {readonly ? 'cursor-not-allowed' : 'cursor-pointer'}"
                        onclick={remove}
                ><Trash2Icon class="inline"/></button>
                </Tooltip>
            </div>
        </div>
    </div>
{/if}

