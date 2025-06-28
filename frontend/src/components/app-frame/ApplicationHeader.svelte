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
Application header that is permanently visible at the top of the screen. Shows the
app title and some information about the quiz.
-->
<script lang="ts">
    import {i18n}         from "../../stores/i18n.js";
    import {pageTitle}    from "../../stores/page.js";
    import {pageSubTitle} from "../../stores/page.js";
</script>

<header>
    <div class="app-name">
        <img src="./logo.png" alt="">
        {$i18n.AppShell.Title}
    </div>
    <div class="quiz-title">
        <span class="title">{$pageTitle}</span>
        <span class="level">{$pageSubTitle}</span>
    </div>
</header>

<style>
    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5em;

        padding: 1rem;

        font-family: "display";
        font-size: 24pt;
    }

    @media all and (width < 700px) {
        header {
            flex-direction: column;
            font-size: 20pt;
        }
    }

    .app-name {
        color: rgb(186, 18, 18);
        text-shadow: 2px 2px 0px black;

        img {
            height: 1.5em;
            vertical-align: middle;
            margin-right: 0.25em;
        }
    }

    .quiz-title {
        color: rgb(18, 116, 186);

        .level {
            font-size: 70%;
            color:rgb(11, 70, 112);
        }
    }
</style>