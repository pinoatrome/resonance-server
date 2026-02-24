<script lang="ts">
    import { raopbridgeApi, type PluginSettingsData } from '$lib/components/raopbridge/raopbridgeApi';
    import Switch from '$lib/components/Switch.svelte'
	import {Loader2, BadgeInfo} from 'lucide-svelte';
    import { toastStore } from '$lib/stores/toast.svelte';

    // Props
    let { settings, readonly = false } = $props();

	const help: Record<string, string> = {
		bin: 'Select one binary among the valid values for your installation',
        pid_file: 'Name of the file with ID of bridge process in the dir of the plugin (readonly)',
        interface: 'Valid address the bridge process will bind, if wrong the plugin will not be active',
        active_at_startup: 'Use this flag to start the bridge process at plugin startup',
        config: 'Name of the file with the configuration of bridge process in the dir of the plugin (readonly)',
        auto_save: 'Option to save the configuration at every scan with a new player',
        logging_enabled: 'Use this to enable logging of bridge process',
        logging_file: 'Name of the file with the logs of bridge process in the dir of the plugin (readonly)',
        debug_enabled: 'Use this flag to debug (requires Logging enabled)',
        debug_category: 'Category of debugging (requires Debug enabled)',
        debug_level: 'Level of debugging (requires Debug enabled)'
    }

	const debugCategoryOptions: Record<string, string> = {
        all: 'ALL',
        slimproto: 'SLIMPROTO',
        stream: 'STREAM',
        decode: 'DECODE',
        output: 'OUTPUT',
        main: 'MAIN',
        util: 'UTIL',
        raop: 'RAOP'
    };

	const debugLevelOptions: Record<string, string> = {
        sdebug: 'TRACE',
        debug: 'DEBUG',
        info: 'INFO',
        warn: 'WARNING',
        error: 'ERROR'
    };

    let binExecutable = $derived(settings.bin);
    let networkInterface = $derived(settings.interface);
	let activeAtStartup = $derived(settings.active_at_startup);
	let autoSave = $derived(settings.auto_save);
	let loggingEnabled = $derived(settings.logging_enabled);
	let debugEnabled = $derived(settings.debug_enabled);
	let debugCategory = $derived(settings.debug_category);
    let debugLevel = $derived(settings.debug_level);

    let binOptions = $state<string[]>([]);
    async function loadBinOptions() {
		try {
			binOptions = await raopbridgeApi.getBinOptions();
		} catch (e) {
			toastStore.error('Failed to load raopbridge bin options', {
				detail: e instanceof Error ? e.message : String(e),
			});
		}
	}
	async function updateSetting(name: string, value: any, validator?: (v: any, previous: any) => Promise<boolean>, previousValue?: any ) {
		if (!!validator){
            const check = await validator(value, previousValue);
			if (!check) {
				toastStore.info(`Invalid value for "${name}": "${value}"`);
			    return;
			}
        }
		const arg : any = {};
		arg[name] = value;
		const result = await raopbridgeApi.updatePluginSettings(arg as Partial<PluginSettingsData>)
        if (result.errors) {
			toastStore.warning(`Server errors: ${result.errors}`);
        } else if (result.result) {
            toastStore.success(`Setting updated`);
			settings = {...settings, ...arg};
        }
    }

	async function checkInterface(value: string | null, previousValue: string | null): Promise<boolean> {
		const parts = value?.split('.') || []
        if (parts.length === 4
            && !parts.find(part => part.length > 3)
            && !parts.find(part => !Number.isInteger(Number(part)))
            && !parts.find(part => Number(part) > 255)) {
			return true;
        }
		networkInterface = previousValue;
		return false;
    }

	// Load valid bin options from the server
	$effect(() => {
        if (!binOptions.length) {
			loadBinOptions();
		}
    });
</script>

{#snippet rowText(label, help_key)}
<div class="grid grid-flow-col grid-rows-2 gap=1">
    <div class="text-lg">{label}</div>
    <div class="text-xs">{help[help_key]}</div>
</div>
{/snippet}

{#if !!settings }
<div>
    <div class="flex flex-1 px-3 py-2">
        <div class="text-lg font-extrabold text-overlay-0 uppercase tracking-wider">Settings</div>
        {#if readonly}
        <div class="ml-10 mt-0 mr-auto text-text">
            <BadgeInfo class="ml-2 inline "/>
            <span class="ml-1 text-sm">Readonly - Deactivate the plugin to change values</span>
        </div>
        {/if}
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>
        {@render rowText('Executable', 'bin')}
        </div>
        <div class="flex-1 text-right">
        {#if !binOptions.length}
            <span class="px-2">{settings.bin}</span><Loader2 size={14} class="animate-spin inline" />
        {:else}
            <select id="bin"
                    onchange="{() => updateSetting('bin', binExecutable)}"
                    disabled={readonly}
                    bind:value={binExecutable}
                    class="px-3 py-1 rounded-lg bg-mantle border border-surface-1 text-text text-lg
                focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer"
            >
            {#each binOptions as value}
                <option value={value}>{value}</option>
            {/each}
            </select>
        {/if}
        </div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('PID Filename', 'pid_file')}</div>
        <div class="flex-1 text-lg text-right">{settings.pid_file}</div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Interface', 'interface')}</div>
        <div class="flex-1 text-right">
            <input type="text"
                   onchange="{() => updateSetting('interface', networkInterface, checkInterface, settings.interface)}"
                   name="raopbridge-interface"
                   placeholder="IP address for raop bridge."
                   bind:value={networkInterface}
                   class="text-center flex-1 px-4 py-1 rounded-xl bg-surface-0 border border-surface-1
                       placeholder-overlay-0 focus:outline-none focus:ring-2
                       focus:ring-accent focus:border-transparent transition-all"
                   disabled={readonly}
            />
        </div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Active @ Startup', 'active_at_startup')}</div>
        <div class="flex flex-1">
            <Switch
                    classes="ml-auto"
                    disabled={readonly}
                    options={['No', 'Yes']}
                    showValue={true}
                    bind:value={activeAtStartup}
                    onToggle={() => updateSetting('active_at_startup', !activeAtStartup)}
            />
        </div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Config File', 'config')}</div>
        <div class="flex-1 text-lg text-right">{settings.config}</div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Auto Save', 'auto_save')}</div>
        <div class="flex flex-1">
            <Switch
                    classes="ml-auto"
                    disabled={readonly}
                    options={['No', 'Yes']}
                    showValue={true}
                    bind:value={autoSave}
                    onToggle={() => updateSetting('auto_save', !autoSave)}
            />
        </div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Logging', 'logging_enabled')}</div>
        <div class="flex flex-1">
            <Switch
                    classes="ml-auto"
                    disabled={readonly}
                    options={['No', 'Yes']}
                    showValue={true}
                    bind:value={loggingEnabled}
                    onToggle={() => updateSetting('logging_enabled', !loggingEnabled)}
            />
        </div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Logging Filename', 'logging_file')}</div>
        <div class="flex-1 text-lg text-right">{settings.logging_file}</div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Debug', 'debug_enabled')}</div>
        <div class="flex flex-1">
            <Switch
                    classes="ml-auto"
                    disabled={readonly}
                    options={['No', 'Yes']}
                    showValue={true}
                    bind:value={debugEnabled}
                    onToggle={() => updateSetting('debug_enabled', !debugEnabled)}
            />
        </div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Debug Category', 'debug_category')}</div>
        <div class="flex-1 text-right">
            <select id="debug-category"
                    onchange="{() => updateSetting('debug_category', debugCategory)}"
                    disabled={readonly}
                    bind:value={debugCategory}
                    class="px-3 py-1 rounded-lg bg-mantle border border-surface-1 text-text text-lg
                    focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer"
            >
                {#each Object.entries(debugCategoryOptions) as [value, label]}
                    <option value={value}>{label}</option>
                {/each}
            </select>
        </div>
    </div>
    <div class="flex flex-1 border border-border m-3 p-5">
        <div>{@render rowText('Debug Level', 'debug_level')}</div>
        <div class="flex-1 text-right">
            <select id="debug-level"
                    onchange="{() => updateSetting('debug_level', debugLevel)}"
                    disabled={readonly}
                    bind:value={debugLevel}
                    class="px-3 py-1 rounded-lg bg-mantle border border-surface-1 text-text text-lg
                    focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer"
            >
                {#each Object.entries(debugLevelOptions) as [value, label]}
                    <option value={value}>{label}</option>
                {/each}
            </select>
        </div>
        <hr class="h-px border border-border" /><hr class="h-px border border-border" />
    </div>
</div>
{/if}
