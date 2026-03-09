<script lang="ts">
	import {type Device, raopbridgeApi, VolumeMode} from '$lib/components/raopbridge/raopbridgeApi';
	import {
		BadgeInfo,
		ChevronDown,
		ChevronUp,
		ListRestartIcon,
		Loader2,
		ShieldQuestionIcon,
		TriangleAlertIcon
	} from 'lucide-svelte';
	import {toastStore} from '$lib/stores/toast.svelte';
	import DeviceCard from './DeviceCard.svelte';
	import DeviceSettings from './DeviceSettings.svelte';
	import Tooltip from "$lib/components/Tooltip.svelte";
	import ModalDialog from "$lib/components/ModalDialog.svelte";

	// Status
    let devices = $state<Device[]>([]);
    let deviceToUpdateInfo = $state<any | null>(null);
    let deviceToRemoveIdx = $state<number | null>(null);
	let deviceToSetupInfo = $state<any | null>(null);
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
            command: field === 'enabled' ? !value ? 'Switch Off' : 'Switch On' : 'Change',
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
		devices[index] = await _doUpdateDevice(instance);
        return true;
	}

	async function _doUpdateDevice(instance: Device): Promise<Device> {
        isNetworking = true;
		const device = await raopbridgeApi.updateDevice(instance);
        isNetworking = false;
        toastStore.success(`Device ${device.name} updated`);
		return device
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

	function setupDevice(idx: number): void {
		deviceToSetupInfo = {
			instance: {...devices[idx]},
			index: idx,
            dirty: false
		}
    }

	function setupDeviceCancel(): void {
		deviceToSetupInfo = null;
    }

	async function setupDeviceConfirm(): Promise<void> {
		if (!deviceToSetupInfo) {
			return;
        }
		if (deviceToSetupInfo.dirty) {
			devices[deviceToSetupInfo.index] = await _doUpdateDevice(deviceToSetupInfo.instance);
        }
		deviceToSetupInfo = null;
    }

    const expandAll = () => expandedFlags = expandedFlags.map(() => true);

	const expandNone = () => expandedFlags = expandedFlags.map(() => false);

    const toggle = (idx: number) => expandedFlags[idx] = !expandedFlags[idx];

	const changeVolumeMode = (v: VolumeMode) => {
		deviceToSetupInfo.instance.common.volume_mode = v;
		if (v === VolumeMode.IGNORED) {
			deviceToSetupInfo.instance.common.volume_feedback = 0;
        } else {
			deviceToSetupInfo.instance.common.volume_feedback = 1;
        }
		deviceToSetupInfo.dirty = true;
	}

    let {readonly} : {readonly: boolean} = $props();

	function reload() {
		loadDevices();
		toastStore.success('Device list reloaded')
    }

	$effect(() => {
		loadDevices();
    });
</script>

<!-- Update Confirmation -->
<ModalDialog
        isOpen={deviceToUpdateInfo !== null}
        inProgress={isNetworking}
        onCancel={updateDeviceCancel}
        onConfirm={updateDeviceConfirm}
>
    <div class="flex items-center justify-center text-lg">
        <ShieldQuestionIcon class="inline text-success" />
        <span class="ml-3">Confirm {deviceToUpdateInfo?.command} {deviceToUpdateInfo?.instance.name} ?</span>
    </div>
</ModalDialog>
<!-- Delete Confirmation -->
<ModalDialog
        isOpen={deviceToRemoveIdx !== null}
        inProgress={isNetworking}
        onCancel={removeDeviceCancel}
        onConfirm={removeDeviceConfirm}
>
    <div class="flex items-center justify-center text-lg">
        <TriangleAlertIcon class="inline text-error" />
        <span class="ml-3">Confirm device removal?</span>
    </div>
</ModalDialog>
<!-- settings dialog -->
<ModalDialog
        isOpen={!!deviceToSetupInfo}
        inProgress={isNetworking}
        onCancel={setupDeviceCancel}
        onConfirm={setupDeviceConfirm}
        title="Device setup"
        headerLine={false}
        hideCancel={true}
        labelOK={'Done'}
>
    <DeviceSettings readonly={readonly}
        device={deviceToSetupInfo?.instance}
        onChangeVolumeMode={changeVolumeMode}
    />
</ModalDialog>
{#if !devices.length}
    <div>Loading... <Loader2 class="animate-spin inline" /></div>
{/if}
<div>
    <div class="flex flex-1 px-3 py-2 items-center">
        <div class="text-lg font-extrabold text-overlay-0 uppercase">Devices</div>
        <Tooltip tip="Reload the list" placement="top">
            <div class="ml-2 text-overlay-0">
                <button class="cursor-pointer bg-surface-0 hover:bg-surface-1 hover:text-accent-hover" onclick={reload}><ListRestartIcon class="inline"/></button>
            </div>
        </Tooltip>
        <div class="flex flex-1 items-center">
            {#if readonly}
            <div class="ml-10 mr-auto text-text">
                <Tooltip tip="Readonly. Deactivate the plugin to change values" placement="top">
                    <BadgeInfo class="ml-2 inline"/>
                </Tooltip>
            </div>
            {/if}
            <div class="flex-1 text-right text-overlay-1 text-xs">
                <button class="mx-2 px-5 py-2 rounded-lg bg-surface-1 hover:bg-surface-0 hover:text-accent-hover transition-colors cursor-pointer"
                        onclick="{expandAll}">Expand All {devices.length}</button>
                <button class="mx-2 px-5 py-2 rounded-lg bg-surface-1 hover:bg-surface-0 hover:text-accent-hover transition-colors cursor-pointer"
                        onclick="{expandNone}">Collapse All {devices.length}</button>
            </div>
        </div>
    </div>
    <div class="px-0 text-lg">
    {#each devices as device, idx}
    <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
        <div class="flex-1">
            <DeviceCard readonly={readonly}
                        device={device}
                        expanded={expandedFlags[idx]}
                        toggle={() => toggle(idx)}
                        remove={() => removeDevice(idx)}
                        rename={(value) => renameDevice(idx, value)}
                        setup={() => setupDevice(idx)}
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

