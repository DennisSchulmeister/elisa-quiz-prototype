<!--
Elisa: AI Learning Assistant
© 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
-->

<!--
@component
A single chat message.
-->
<script lang="ts">
    import markdownit         from "markdown-it";
    import type {ChatMessage} from "../../../stores/chat.js";
    import AvatarAgent        from "./avatar-agent.png";
    import AvatarUser         from "./avatar-user.png";
    import AvatarError        from "./avatar-error.png";

    interface Props {
        message: ChatMessage;
        parent:  HTMLDivElement;
    }

    let {message = {}, parent}: Props = $props();

    let avatar = $state(AvatarAgent);
    if (message.role === "user")  avatar = AvatarUser;
    if (message.role === "error") avatar = AvatarError;

    let md = markdownit();
    
    let messageText = $derived.by(() => {
        if (typeof message.text === "string") {
            return md.render(message.text || "");
        }
    });

    $effect.pre(() => {
        window.setTimeout(() => {
            parent.scrollTop = parent.scrollHeight;
        }, 500);
    });
</script>

<div id="container" class={message.role}>
    <img src={avatar} alt="" class="avatar">

    <div class="message">
        {@html messageText}
    </div>
</div>

<style>
    #container {
        display: flex;
        flex-direction: row;
        justify-content: start;
        align-items: start;
        gap: 2em;

        backdrop-filter: blur(3px);
        padding: 1em;
        border: 1px solid rgba(0,0,0, 0.05);
        border-radius: 0.5em;

        & > .avatar {
            display: block;
            width: 5em;
        }

        & > .message {
            flex: 1;
        }

        &.error {
            color: darkred;
        }

        &.user {
            color: darkblue;
        }

        &.agent {
            color: rgb(60, 60, 60);
        }
    }
</style>