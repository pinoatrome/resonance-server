<script lang="ts">
	import {Loader2} from 'lucide-svelte';
	import {toastStore} from '$lib/stores/toast.svelte';
	import Tabs from '$lib/components/Tabs.svelte';
	import {raopbridgeApi, type PluginStatus} from './raopbridgeApi';
	import SettingsView from "./SettingsView.svelte";
	import StatusView from "./StatusView.svelte";
	import ToggleBridgeStatus from "./ToggleBridgeStatus.svelte";
	import DeviceList from "./DeviceList.svelte";
	import AboutView from "./AboutView.svelte";

	const { info, tab = null } = $props();

	let pluginStatus = $state<PluginStatus | null>(null);
	let activeTab = $state<number | null>(null);
	let readonly = $derived<boolean>(true);

	async function loadPluginStatus() {
		try {
			pluginStatus = await raopbridgeApi.getPluginStatus();
			readonly = pluginStatus?.bridge === 'active';
		} catch (e) {
			toastStore.error('Failed to load raopbridge plugin status', {
				detail: e instanceof Error ? e.message : String(e),
			});
		}
	}
	async function togglePluginStatus(): Promise<boolean> {
		if (!pluginStatus) {
			throw new Error('Invalid plugin status');
        }
		let result: boolean | null;
		if (pluginStatus.bridge === 'active') {
			result = await raopbridgeApi.deactivate();
			if (result) {
				pluginStatus.bridge = 'inactive'
            }
		} else if (pluginStatus.bridge === 'inactive') {
			result = await raopbridgeApi.activate();
            if (result) {
				pluginStatus.bridge = 'active'
            }
		} else {
			result = null;
        }
		if (result === null) {
			throw new Error(`Invalid bridge status: ${pluginStatus.bridge}`);
		}
		readonly = pluginStatus?.bridge === 'active';
        return result;
    }

	// Load pluginStatus and optionally the tab index to show
	$effect(() => {
        loadPluginStatus();

        if (activeTab == null) {
            activeTab = !!tab ? Number(tab) : 0;
        }
	});
</script>
<div class="flex overflow-hidden">
    {#if !pluginStatus}
        <div>Loading....
            <Loader2 size={14} class="animate-spin inline"/>
        </div>
    {:else}
        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col min-w-0 bg-base glass">
            <!-- Header -->
            <header class="px-6 py-4">
                <div class="flex items-center justify-between">
                    <StatusView info={info}/>
                    <ToggleBridgeStatus status={pluginStatus} onToggle={togglePluginStatus}/>
                </div>
            </header>
            <!-- Content -->
            <div class="flex-1 flex overflow-hidden">
                <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
                    <!-- navigation tabs -->
                    <div class="text-text ml-1">
                        <Tabs active={activeTab || 0} onchange={(evt) => activeTab = evt}
                              pages={['Devices', 'Settings', 'Logs', 'About']}/>
                    </div>
                    <div class="px-6 py-4 bg-base/50 backdrop-blur-sm z-10">
                        {#if activeTab === 0} <!-- Registered devices -->
                            <DeviceList readonly={readonly}/>
                        {:else if activeTab === 1} <!-- Plugin settings -->
                            <SettingsView readonly={readonly}/>
                        {:else if activeTab === 2} <!-- Bridge logging -->
                            <div class="w-100 h-100"> TODO </div>
                        {:else if activeTab === 3} <!-- About -->
                            <AboutView/>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>
