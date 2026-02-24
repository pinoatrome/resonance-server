<script lang="ts">
    import { onMount } from 'svelte';
    import Settings from "$lib/components/raopbridge/Settings.svelte";
    import Status from "$lib/components/raopbridge/Status.svelte";
    import ToggleBridgeStatus from "$lib/components/raopbridge/ToggleBridgeStatus.svelte";

    let pluginInfo: any;
    let pluginStatus: any;

    onMount(()=>{
        pluginInfo = {name: 'raopbridge', version: '0.0.1'};
        pluginStatus = {
            plugin: "running",
            bridge: "active",
            settings: {
                bin: 'squeeze2raop-macos-arm64-static',
                interface: '192.168.1.65',
                config: 'squeeze2raop.xml',
                active_at_startup: true,
                auto_save: true,
                logging_enabled: true,
                debug_enabled: false,
                debug_category: 'all',
                debug_level: 'info',
                logging_file: 'squeeze2raop.log',
                pid_file: 'squeeze2raop.pid'
            }
        }
    });
</script>
<div class="flex h-screen overflow-hidden">
  <!-- Main Content Area -->
  <div class="flex-1 flex flex-col min-w-0 bg-base">
    <!-- Header -->
    <header class="glass border-b border-border px-6 py-4">
      <div class="flex items-center justify-between gap-4">
          <Status info={pluginInfo} status={pluginStatus} />
          <ToggleBridgeStatus status={pluginStatus} />
      </div>
    </header>
    <!-- Content -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Plugin settings -->
      <main class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
          <div class="px-6 py-4 border-b border-border bg-base/50 backdrop-blur-sm z-10">
              <Settings settings={pluginStatus?.settings} />
          </div>
      </main>
    </div>
  </div>
</div>
