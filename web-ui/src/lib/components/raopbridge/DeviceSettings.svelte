<script lang="ts">
    import {Airplay} from 'lucide-svelte';
    import {VolumeMode, type Device} from "$lib/components/raopbridge/raopbridgeApi";
    let {device, onChangeVolumeMode, readonly} : {
		device: Device,
        onChangeVolumeMode: (v: VolumeMode) => void,
        readonly: boolean
	} = $props();
	let deviceVolumeMode = $derived<number>(device.common.volume_mode)
</script>
<div class="flex flex-1 flex-col gap-10 text-lg">
    <div class="mb-3 py-3">
        <div class="text-sm">Audio device</div>
        <div class="p-2"><Airplay class="inline mr-3" />{device.name}</div>
    </div>
    <div class="flex flex-1">
        <div>Volume control</div>
        <div class="flex-1 text-right">
            <select id="volumeControl"
                    disabled={readonly}
                    onchange={() => onChangeVolumeMode(deviceVolumeMode)}
                    bind:value={deviceVolumeMode}
                    class="px-3 py-1 rounded-lg bg-mantle border border-surface-1 text-text
                focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer"
            >
                <option value={VolumeMode.HARDWARE}>Device volume</option>
                <option value={VolumeMode.IGNORED}>Fixed volume</option>
                <option value={VolumeMode.SOFTWARE}>Gain on samples</option>
            </select>
        </div>
    </div>
</div>
