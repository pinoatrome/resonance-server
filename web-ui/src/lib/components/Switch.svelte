<script lang="ts">
    // based on suggestions from:
    // Inclusive Components by Heydon Pickering https://inclusive-components.design/toggle-button/
    // On Designing and Building Toggle Switches by Sara Soueidan https://www.sarasoueidan.com/blog/toggle-switch-design/
    /*
        There are 3 usable layouts: inner, multi, slider (* default *)

        <Switch bind:value={switchValue} label="Enable dark mode" design="inner" />
        <p>
            Switch is {switchValue}
        </p>
        <Switch bind:value={multiValue} label="Choose a theme" design="multi" options={['light', 'dark']} fontSize={12}/>
        <p>
            Switch is {multiValue}
        </p>
        <Switch bind:value={sliderValue} label="Enable dark mode" fontSize={24} design="slider" />
        <p>
            Switch is {sliderValue}
        </p>
     */

   /** @type {Props} */
   let {
       label = null,
       design = 'slider',
       classes = '',
       options = ['off', 'on'],
       fontSize = 16,
       value = $bindable<boolean>(),
       disabled = false,
       showValue = false,
       onToggle = () => {}
   } = $props();

    const uniqueID = Math.floor(Math.random() * 100)
</script>

{#if design === 'inner'}
<div class="s s--inner {classes}">
    <span id={`switch-${uniqueID}`}>{label}</span>
    <button
        disabled={disabled}
        role="switch"
        aria-checked={value ? 'true' : 'false'}
        aria-labelledby={`switch-${uniqueID}`}
        onclick={() => onToggle()}>
            <span>{options[1]}</span>
            <span>{options[0]}</span>
    </button>
</div>
{:else if design === 'multi'}
<div class="s s--multi {classes}">
    <div role='radiogroup'
         class="group-container"
         aria-labelledby={`label-${uniqueID}`}
         style="font-size:{fontSize}px"
         id={`group-${uniqueID}`}>
    <div class='legend' id={`label-${uniqueID}`}>{label}</div>
        {#each options as option}
            <input disabled={disabled} type="radio" id={`${option}-${uniqueID}`} value={option} bind:group={value}>
            <label for={`${option}-${uniqueID}`}>
                {option}
            </label>
        {/each}
    </div>
</div>
{:else}
<div class="s s--slider {classes}" style="font-size:{fontSize}px">
    <span id={`switch-${uniqueID}`}>{label}</span>
    <button
        disabled={disabled}
        role="switch"
        aria-checked={!!value ? 'true' : 'false'}
        aria-labelledby={`switch-${uniqueID}`}
        onclick={() => onToggle()}>
    </button>
    <span class="legend">{#if showValue}{!value ? options[0] : options[1]}{/if}</span>
</div>
{/if}

<style>
    /* Inner Design Option */
    .s--inner button {
        padding: 0.5em;
        background-color: #fff;
        border: 1px solid var(--color-surface-0);
    }
    [role='switch'][aria-checked='true'] :first-child,
    [role='switch'][aria-checked='false'] :last-child {
        display: none;
        color: #fff;
    }

    .s--inner button span {
        user-select: none;
        pointer-events:none;
        padding: 0.25em;
    }

    /* Multi Design Option */

    /* Based on suggestions from Sara Soueidan https://www.sarasoueidan.com/blog/toggle-switch-design/
    and this example from Scott O'hara https://codepen.io/scottohara/pen/zLZwNv */

    .s--multi .group-container {
        border: none;
        padding: 0;
        white-space: nowrap;
    }

    /* .s--multi legend {
    font-size: 2px;
    opacity: 0;
    position: absolute;
    } */

    .s--multi label {
        display: inline-block;
        line-height: 1.6;
        position: relative;
        z-index: 2;
    }

    .s--multi input {
        opacity: 0;
        position: absolute;
    }

    .s--multi label:first-of-type {
        padding-right: 5em;
    }

    .s--multi label:last-child {
        margin-left: -5em;
        padding-left: 5em;
    }

    .s--multi:focus-within label:first-of-type:after {
        box-shadow: 0 0 8px var(--accent-color);
        border-radius: 1.5em;
    }

    /* making the switch UI.  */
    .s--multi label:first-of-type:before,
    .s--multi label:first-of-type:after {
        content: "";
        height: 1.25em;
        overflow: hidden;
        pointer-events: none;
        position: absolute;
        vertical-align: middle;
    }

    .s--multi label:first-of-type:before {
        border-radius: 100%;
        z-index: 2;
        position: absolute;
        width: 1.2em;
        height: 1.2em;
        background: #fff;
        top: 0.2em;
        right: 1.2em;
        transition: transform 0.3s;
    }

    .s--multi label:first-of-type:after {
        background: var(--accent-color);
        border-radius: 1em;
        margin: 0 1em;
        transition: background .2s ease-in-out;
        width: 3em;
        height: 1.6em;
    }

    .s--multi input:first-of-type:checked ~ label:first-of-type:after {
        background: var(--color-surface-0);
    }

    .s--multi input:first-of-type:checked ~ label:first-of-type:before {
        transform: translateX(-1.4em);
    }

    .s--multi input:last-of-type:checked ~ label:last-of-type {
        z-index: 1;
    }

    .s--multi input:focus {
        box-shadow: 0 0 8px var(--accent-color);
        border-radius: 1.5em;
    }

    .s--inner button:focus {
        outline: var(--accent-color) solid 1px;
    }

    /* Slider Design Option */

    .s--slider {
        display: flex;
        align-items: center;
    }

    .s--slider button {
        width: 3em;
        height: 1.6em;
        position: relative;
        margin: 0 0 0 0.5em;
        background: var(--color-surface-2);
        border: none;
        cursor: pointer;
    }

    .s--slider button::before {
        content: '';
        position: absolute;
        width: 1.3em;
        height: 1.3em;
        background: #fff;
        top: 0.13em;
        right: 1.5em;
        transition: transform 0.3s;
    }

    .s--slider button:disabled {
        cursor: not-allowed;
        background: var(--color-overlay-0);
    }

    .s--slider button[aria-checked='true'] {
        background-color: var(--color-accent);
    }

    .s--slider button[aria-checked='true']:disabled {
        background-color: var(--color-overlay-0);
    }



    .s--slider button[aria-checked='true']::before{
        transform: translateX(1.3em);
        transition: transform 0.3s;
    }

    .s--slider button:focus {
        box-shadow: 0 0 0 1px var(--accent-color);
    }

    .s--slider .legend {
        margin-left: 1.0em;
        padding: 0.25em;
    }

    /* gravy */

    /* Inner Design Option */
    [role='switch'][aria-checked='true'] :first-child,
    [role='switch'][aria-checked='false'] :last-child {
        border-radius: 0.25em;
        background: var(--accent-color);
        display: inline-block;
    }

    .s--inner button:focus {
        box-shadow: 0 0 8px var(--accent-color);
        border-radius: 0.1em;
    }

    /* Slider Design Option */
    .s--slider button {
        border-radius: 1.5em;
    }

    .s--slider button::before {
        border-radius: 100%;
    }

    .s--slider button:focus {
        box-shadow: 0 0 8px var(--accent-color);
        border-radius: 1.5em;
    }


</style>
