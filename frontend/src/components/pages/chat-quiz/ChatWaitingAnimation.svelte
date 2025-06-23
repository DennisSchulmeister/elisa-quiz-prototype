<!--
Elisa: AI Learning Quiz
© 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
-->

<!--
@component
Small animation to indicate that we are waiting on the backend to generate
a chat message for us.
-->
<script lang="ts">
    import AvatarAi from "./avatar-ai.png";
    import {i18n}    from "../../../stores/i18n.js";

    let {size = "small"} = $props();
    let width = $derived(size === "big" ? "15em" : "7em");
</script>

<img src={AvatarAi} alt="{$i18n.Chat.Waiting}" style:max-width={width}>

<style>
    img {
        display: block;
        animation: spinning 1s ease-in-out alternate infinite;
    }

    @keyframes spinning {
        0% {
            transform: rotate3d(0,1,0.4, -15deg);
        }

        100% {
            transform: rotate3d(0,1,0.2, 20deg);
        }
    }
</style>