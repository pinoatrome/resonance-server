<script lang="ts">
    import Switch from '$lib/components/Switch.svelte'
    // Props
	let { settings }: { settings: any} = $props();
</script>
{#if !!settings }
    <div class="">
    <div class="px-3 py-2 text-lg font-extrabold text-overlay-0 uppercase tracking-wider mb-2">setup</div>
    <div class="text-lg grid grid-flow-row grid-cols-2 content-start content-stretch gap-2">
        <div>Executable:</div><div>{settings.bin}</div>
        <div>PID Filename:</div><div>{settings.pid_file}</div>
        <div>Interface:</div><div>{settings.interface}</div>
        <div>Active @ Startup:</div><div><Switch label="" design="multi" options={['off', 'on']} value={settings.active_at_startup  ? 'on' : 'off'} /></div>
        <div>Config File:</div><div>{settings.config}</div>
        <div>Auto-Save:</div><div><Switch label="" design="multi" options={['off', 'on']} value={settings.auto_save  ? 'on' : 'off'} /></div>
        <div>Logging:</div><div><Switch label="" design="multi" options={['off', 'on']} value={settings.logging_enabled  ? 'on' : 'off'} /></div>
        <div>Logging Filename:</div><div>{settings.logging_file}</div>
        <div>Debug:</div><div><Switch label="" design="multi" options={['off', 'on']} value={settings.debug_enabled  ? 'on' : 'off'} /></div>
        <div>Debug Category:</div><div>{settings.debug_category}</div>
        <div>Debug Level:</div><div>{settings.debug_level}</div>
        </div>
    </div>
{/if}
