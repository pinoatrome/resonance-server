<script lang="ts">
	import {raopbridgeApi, type Device} from '$lib/components/raopbridge/raopbridgeApi';
	import {ListRestartIcon, ChevronDown, ChevronUp, Loader2, ShieldQuestionIcon, TriangleAlertIcon, BadgeInfo} from 'lucide-svelte';
    import {toastStore} from '$lib/stores/toast.svelte';
    import DeviceCard from './DeviceCard.svelte';
	import ModalDlg from "./ModalDlg.svelte";

    // Status
    let devices = $state<Device[]>([]);
    let deviceToUpdateInfo = $state<any | null>(null);
    let deviceToRemoveIdx = $state<number | null>(null);
	let isNetworking = $state<boolean>(false);
	let expandedFlags = $state<boolean[]>([]);

    async function loadDevices() {
		try {
			isNetworking = true;
			devices = await raopbridgeApi.getDevices();
			isNetworking = false;
			expandedFlags = devices.map(() => false);
		} catch (e) {
			toastStore.error('Failed to load raopbridge devices', {
				detail: e instanceof Error ? e.message : String(e),
			});
		}
	}
	function updateDevice(idx: number, field: string , value: boolean | string): void {
		const arg: any = {};
		arg[field] = value;
		deviceToUpdateInfo = {
			instance: {...devices[idx], ...arg} as Device,
			index: idx,
			field: field,
			value: value,
            command: field === 'enabled' ? !value ? 'Switch Off' : 'Switch On' : 'Change'
		}
    }

	function updateDeviceCancel(): void {
		deviceToUpdateInfo = null;
	}

	async function updateDeviceConfirm(): Promise<void> {
        if (!deviceToUpdateInfo) {
			return;
        }
		isNetworking = true;
		const device = await raopbridgeApi.updateDevice(deviceToUpdateInfo.instance)
        devices[deviceToUpdateInfo.index] = device;
        isNetworking = false;
		deviceToUpdateInfo = null;
        toastStore.success(`Device ${device.name} updated`);
    }

	async function renameDevice(index: number, value: string): Promise<boolean> {
		const duplicated = devices.filter((_, idx) => idx !==index).find((item) => item.name === value);
		if (!!duplicated) {
			toastStore.warning(`Device ${value} already used`);
			return false;
        }
        const instance = {...devices[index], name: value};
		isNetworking = true;
		const device = await raopbridgeApi.updateDevice(instance);
        devices[index] = device;
        isNetworking = false;
        toastStore.success(`Device ${device.name} updated`);
		return true
	}

	function removeDevice(idx: number): void {
		deviceToRemoveIdx = idx;
    }

	function removeDeviceCancel(): void {
		deviceToRemoveIdx = null;
    }

	async function removeDeviceConfirm(): Promise<void> {
		if (deviceToRemoveIdx === null) {
			return
		}
		isNetworking = true;
		const deviceToRemove = devices[deviceToRemoveIdx]
		const result = await raopbridgeApi.deleteDevice(deviceToRemove)
        isNetworking = false;
        if (result) {
            devices.splice(deviceToRemoveIdx, 1);
			toastStore.success(`Device ${deviceToRemove.name} removed`);
        }
		deviceToRemoveIdx = null;
    }

    const expandAll = () => {expandedFlags = expandedFlags.map(() => true)}

	const expandNone = () => {expandedFlags = expandedFlags.map(() => false)}

    const toggle = (idx: number) => {expandedFlags[idx] = !expandedFlags[idx]};

    let {readonly} = $props();

	function reload() {
		loadDevices();
		toastStore.success('Device list reloaded')
    }

	$effect(() => {
		loadDevices();
    });
</script>

<!-- Update Confirmation -->
<ModalDlg
        isOpen={deviceToUpdateInfo !== null}
        inProgress={isNetworking}
        onCancel={updateDeviceCancel}
        onConfirm={updateDeviceConfirm}
>
    <div class="flex items-center justify-center text-lg">
        <ShieldQuestionIcon class="inline text-success" />
        <span class="ml-3">Confirm {deviceToUpdateInfo?.command} {deviceToUpdateInfo?.instance.name} ?</span>
    </div>
</ModalDlg>
<!-- Delete Confirmation -->
<ModalDlg
        isOpen={deviceToRemoveIdx !== null}
        inProgress={isNetworking}
        onCancel={removeDeviceCancel}
        onConfirm={removeDeviceConfirm}
>
    <div class="flex items-center justify-center text-lg">
        <TriangleAlertIcon class="inline text-error" />
        <span class="ml-3">Confirm device removal?</span>
    </div>
</ModalDlg>

{#if !devices.length}
    <div>Loading... <Loader2 class="animate-spin inline" /></div>
{/if}
<div>
    <div class="flex px-3 py-2 mb-2">
        <div class="text-lg font-extrabold text-overlay-0 uppercase">Devices</div>
        <div class="ml-2 text-overlay-0">
            <button class="cursor-pointer bg-surface-0 hover:bg-surface-1 hover:text-accent-hover" onclick={reload}><ListRestartIcon class="inline"/></button>
        </div>
        <div class="flex flex-1">
            {#if readonly}
            <div class="ml-10 mt-0 mr-auto text-text">
                <BadgeInfo class="ml-2 inline"/>
                <span class="ml-1 text-sm">Readonly - Deactivate the plugin to change values</span>
            </div>
            {/if}
            <div class="ml-auto mr-0 text-end text-overlay-1">
                <button class="mx-2 px-5 py-2 rounded-lg bg-surface-1 hover:bg-surface-0 hover:text-accent-hover transition-colors cursor-pointer"
                        onclick="{expandAll}">Expand All {devices.length}</button>
                <button class="mx-2 px-5 py-2 rounded-lg bg-surface-1 hover:bg-surface-0 hover:text-accent-hover transition-colors cursor-pointer"
                        onclick="{expandNone}">Collapse All {devices.length}</button>
            </div>
        </div>
    </div>
    <div class="px-5 text-lg">
    {#each devices as device, idx}
    <div class="flex border border-border m-3 p-5">
        <div class="flex-1">
            <DeviceCard readonly={readonly}
                        device={device}
                        expanded={expandedFlags[idx]}
                        toggle={() => toggle(idx)}
                        remove={() => removeDevice(idx)}
                        rename={(value: String) => renameDevice(idx, value)}
                        update={(f, v) => updateDevice(idx, f, v)}
            />
        </div>
        <div class="text-end relative">
            <button class="absolute top-0 right-0 p-1 cursor-pointer" onclick={() => toggle(idx)}>
            {#if expandedFlags[idx]}
                <ChevronUp class="inline"/>
            {:else}
                <ChevronDown class="inline"/>
            {/if}
            </button>
        </div>
    </div>
    {/each}
    </div>
</div>

