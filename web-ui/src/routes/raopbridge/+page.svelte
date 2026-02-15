<script lang="ts">

import {page} from "$app/state";
import PluginPage from "$lib/components/raopbridge/PluginPage.svelte";

let info = $state<any>({
	name: 'raopbridge',
    version: '0.0.1',
    description: 'Bridge squeeze2raop version: v1.8.5',
});

let tab = $state<string | null>(page.url.searchParams.get('tab'));

</script>

<PluginPage info={info} tab={tab}/>
