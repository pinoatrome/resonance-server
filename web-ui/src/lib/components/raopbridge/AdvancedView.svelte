<script lang="ts">
	import {type CommonOptions, raopbridgeApi, VolumeMode} from "$lib/components/raopbridge/raopbridgeApi";
	import {toastStore} from "$lib/stores/toast.svelte";

	let {readonly} = $props();
	let advanced = $state<CommonOptions>();

	async function loadAdvancedSettings() {
		try {
			advanced = await raopbridgeApi.getPluginAdvancedSettings();
		} catch (e) {
			toastStore.error('Failed to load raopbridge plugin settings', {
				detail: e instanceof Error ? e.message : String(e),
			});
		}
	}

	const displayVolumeMode = (v: VolumeMode) => v === VolumeMode.IGNORED ? 'Fixed' : v === VolumeMode.HARDWARE ? 'Device' : 'Gain';
	const displayVolumeMapping = (v: [number, number][]) => v.map((value) => `[${value}]`).join(' ');

	// Load data from the server
	$effect(() => {
		loadAdvancedSettings();
	});
</script>

{#if !!advanced}
    <div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Streambuf size</div>
            <div class="flex-1 text-right">{advanced.streambuf_size}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Output size</div>
            <div class="flex-1 text-right">{advanced.output_size}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Enabled</div>
            <div class="flex-1 text-right">{advanced.enabled}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Codecs</div>
            <div class="flex-1 text-right">{advanced.codecs}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Sample rate</div>
            <div class="flex-1 text-right">{advanced.sample_rate}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Resolution</div>
            <div class="flex-1 text-right">{advanced.resolution}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Resample</div>
            <div class="flex-1 text-right">{advanced.resample}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Resample options</div>
            <div class="flex-1 text-right">{advanced.resample_options}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Volume mode</div>
            <div class="flex-1 text-right">{displayVolumeMode(advanced.volume_mode)}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Player volume</div>
            <div class="flex-1 text-right">{advanced.player_volume}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Volume mapping</div>
            <div class="flex-1 text-right">{displayVolumeMapping(advanced.volume_mapping)}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Volume feedback</div>
            <div class="flex-1 text-right">{advanced.volume_feedback}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Mute on pause</div>
            <div class="flex-1 text-right">{advanced.mute_on_pause}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Send metadata</div>
            <div class="flex-1 text-right">{advanced.send_metadata}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Send coverart</div>
            <div class="flex-1 text-right">{advanced.send_coverart}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Auto play</div>
            <div class="flex-1 text-right">{advanced.auto_play}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Idle timeout (sec)</div>
            <div class="flex-1 text-right">{advanced.idle_timeout}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Remove timeout</div>
            <div class="flex-1 text-right">{advanced.remove_timeout}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>ALAC encode</div>
            <div class="flex-1 text-right">{advanced.alac_encode}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Encryption</div>
            <div class="flex-1 text-right">{advanced.encryption}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Read ahead</div>
            <div class="flex-1 text-right">{advanced.read_ahead}</div>
        </div>
        <div class="flex flex-1 rounded-lg border border-border m-3 p-5">
            <div>Server</div>
            <div class="flex-1 text-right">{advanced.server}</div>
        </div>
    </div>
{/if}
