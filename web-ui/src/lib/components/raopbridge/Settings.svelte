<script lang="ts">
    // Props
	let { settings }: { settings: any} = $props();
</script>
{#if !!settings }
    <div>executable: {settings.bin}</div>
    <div>interface: {settings.interface}</div>
    <div>active_at_startup: {settings.active_at_startup}</div>
    <div>auto_save: {settings.auto_save}</div>
    <div>config file: {settings.config}</div>
    <div>pid file: {settings.pid_file}</div>
    <div>logging: {settings.logging_enabled}</div>
    <div>logging file: {settings.logging_file}</div>
    <div>debug: {settings.debug_enabled}</div>
    <div>debug category: {settings.debug_category}</div>
    <div>debug level: {settings.debug_level}</div>
{/if}
