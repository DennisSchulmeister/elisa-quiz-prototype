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
Main container for the chat conversation.
-->
<script lang="ts">
    // https://fonts.google.com/icons?selected=Material+Symbols+Outlined:arrow_upward
    import ArrowUp     from "./google-material-arrow-up.svg";
    import ChatMessage from "./ChatMessage.svelte";
    import {i18n}      from "../../../stores/i18n.js";
    import {chat}      from "../../../stores/chat.js";

    let inputInnerDiv: HTMLDivElement;
    let readyToSend = $state(false);

    function focusInputInnerDiv() {
        inputInnerDiv.focus();
    }

    function updateInputState() {
        readyToSend = (inputInnerDiv.textContent !== null) && (inputInnerDiv.textContent.trim() !== "");
    }

    function onInputKeyUp(event: KeyboardEvent) {
        updateInputState();
        
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    }

    function sendMessage() {
        if (inputInnerDiv.textContent) {
            chat.sendChatMessage(inputInnerDiv.textContent);
            inputInnerDiv.textContent = "";
        }

        updateInputState();
    }
</script>

<div id="container">
    <!-- Chat messages -->
    <div id="messages">
        {#each $chat as chatMessage}
            <ChatMessage message={chatMessage}/>
        {/each}
    </div>

    <!-- User input field -->
    <div
        id       = "user-input"
        role     = "dialog"
        tabindex = "0"
        onclick  = {focusInputInnerDiv}
        onkeyup  = {onInputKeyUp}
        onblur   = {updateInputState}
    >
        <div class="input-field-placeholder">
            <div
                class           = "input-field"
                contenteditable = "true"
                role            = "textbox"
                tabindex        = "0"
                onkeyup         = {onInputKeyUp}
                bind:this       = {inputInnerDiv}
            ></div>
    
            {#if !readyToSend}
                <div class="placeholder">
                    {$i18n.Chat.Placeholder}
                </div>
            {/if}
        </div>

        <button
            title        = {$i18n.Chat.TooltipSend}
            class:active = {readyToSend}
            onclick      = {sendMessage}
        >
            <img src={ArrowUp} alt={$i18n.Chat.TooltipSend}>
        </button>
    </div>
</div>

<style>
    #container {
        flex: 1;

        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: stretch;
        gap: 2em;
    }

    #messages {
        display: flex;
        flex-direction: column;
        gap: 1em;

        overflow-y: auto;
    }

    #user-input {
        border: 1px solid lightgrey;
        background: white;
        box-shadow: 1px 1px 5px rgba(0,0,0, 0.25);
        color: rgb(60,60,60);

        padding: 1em;
        border-radius: 0.5em;

        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: end;
        gap: 2em;

        .input-field-placeholder > *{
            display: inline-block;
            border: none;
            outline: none;
        }

        .placeholder {
            color: grey;
        }

        button {
            width: 3em;
            height: 3em;
            border-radius: 100%;

            border: none;
            background: lightgrey;

            &.active {
                background: grey;

                cursor: pointer;
                background-color: rgb(60, 60, 60);
                transition: background-color 0.25s;

                &:hover {
                    background-color: rgb(80, 80, 80);
                }
            }

            img {
                display: block;
                width: 100%;
            }
        }
    }
</style>