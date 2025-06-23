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
Main page with the chat conversation and the quiz game.
-->
<script lang="ts">
    import Chat           from "./Chat.svelte"
    import Quiz           from "./Quiz.svelte"

    import {i18n}         from "../../../stores/i18n.js";
    import QuizStore      from "../../../stores/quiz.js";
    import {pageTitle}    from "../../../stores/page.js";
    import {pageSubTitle} from "../../../stores/page.js";

    $pageTitle    = $QuizStore.subject;
    $pageSubTitle = $QuizStore.level;
    
    let mobileShowChat = $state(true);

    function toggleMobileView(event: MouseEvent) {
        mobileShowChat = !mobileShowChat;
        event.preventDefault();
    }
</script>

<div id="main_area">
    {#if $QuizStore.running}
        <section class="quiz {mobileShowChat ? 'mobileHidden' : ''}">
            <a href="#dummy" class="toggle_view" onclick={toggleMobileView}>
                {$i18n.Quiz.MobileShowChat}
            </a>

            <Quiz/>
        </section>
    {/if}

    <section class="chat {mobileShowChat ? '' : 'mobileHidden'}">
        {#if $QuizStore.running}
            <a href="#dummy" class="toggle_view" onclick={toggleMobileView}>
                {$i18n.Chat.MobileShowQuiz}
            </a>
        {/if}

        <Chat/>
    </section>
</div>
<div>
    <a href="#/">{$i18n.AppShell.ChooseLanguage}</a>
</div>

<style>
    #main_area {
        flex: 1;
        display: flex;
        flex-direction: row;
        justify-content: center;

        box-sizing: border-box;
        min-height: 100%;
        max-height: 100%;
    }

    section {
        display: flex;
        flex-direction: column;
        justify-content: stretch;
        align-items: stretch;
        gap: 0.5em;

        box-sizing: border-box;
        min-height: 100%;
        max-height: 100%;
        
        width: 100%;
    }

    a {
        font-size: 90%;
    }

    @media all and (width < 700px) {
        .mobileHidden {
            display: none;
        }
    }

    @media all and (width >= 700px) {
        section {
            .toggle_view {
                display: none;
            }

            &.quiz {
                flex: 2;
            }

            &.chat {
                flex: 1;
                max-width: 65em;
            }
        }
    }
</style>