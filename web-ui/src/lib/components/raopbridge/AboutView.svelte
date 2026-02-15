<script lang="ts">

import {Blocks} from "lucide-svelte";
</script>
<div class="mb-40">
    <div class="flex flex-1 px-3 py-2 items-center">
        <div class="text-lg font-extrabold text-overlay-0 uppercase tracking-wider">About</div>
    </div>
    <div class="px-0 text-lg">
        <div class="flex rounded-lg border border-border m-3 p-5">
            <div class="flex-1 flex-col mb-3 p-3 items-start justify-end">
                <div class="mb-2 text-sm text-overlay-0">Plugin</div>
                <div class="text-sm">
                    <div class="p-5 mb-3 text-text"><Blocks class="inline mr-3" />Airplay Bridge</div>
                    <div class="my-3 text-overlay-0">
                        <div>Airplay adapter for resonance server</div>
                        <div>Each connected device will be 'bridged' to the Resonance server as a SqueezeBox device</div>
                    </div>
                    <div class="mt-5 text-overlay-0">
                        <div>The code repository is maintained by Pinoatrome <a href="https://github.com/pinoatrome/resonance-server" target="_blank"><span class="underline">here</span></a>.</div>
                        <div>Use the repository to open issues or to request support - Feedback is most welcome!</div>
                    </div>
                    <div class="mt-5 text-accent">The implementation is a porting on python language of <a href="https://github.com/philippe44/LMS-Raop" target="_blank"><span class="underline">LMS-Raop plugin</span></a> by philippe44 </div>
                </div>
            </div>

        </div>
    </div>
</div>
