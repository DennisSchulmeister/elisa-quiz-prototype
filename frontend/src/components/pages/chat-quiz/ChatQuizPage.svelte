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
    import Chat          from "./Chat.svelte"
    import Quiz          from "./Quiz.svelte"
    import {i18n}        from "../../../stores/i18n.js";
    import {quizRunning} from "../../../stores/quiz.js";

    let mobileShowChat = $state(true);

    function toggleMobileView() {
        mobileShowChat = !mobileShowChat;
    }
</script>

<div id="main_area">
    {#if $quizRunning}
        <section class="quiz {mobileShowChat ? 'mobileHidden' : ''}">
            <a href="#top" class="toggle_view" onclick={toggleMobileView}>
                {$i18n.Quiz.MobileShowChat}
            </a>

            <Quiz/>
        </section>
    {/if}

    <section class="chat {mobileShowChat ? '' : 'mobileHidden'}">
        <a href="#top" class="toggle_view" onclick={toggleMobileView}>
            {$i18n.Chat.MobileShowQuiz}
        </a>

        <Chat/>
    </section>
</div>

<style>
    #main_area {
        flex: 1;
        display: flex;
        flex-direction: row;
        justify-content: center;
    }

    section {
        display: flex;
        flex-direction: column;
        justify-content: stretch;
        align-items: stretch;
        gap: 0.5em;

        width: 100%;

        .toggle_view {
            font-size: 90%;
            color: darkblue;
            text-decoration: none;
            text-align: center;
        }
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