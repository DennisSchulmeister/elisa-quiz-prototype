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
Start view to choose the main UI language.
-->
<script lang="ts">
    // https://pixabay.com/illustrations/flag-of-germany-flag-german-flag-1060305/
    // https://pixabay.com/illustrations/flag-united-kingdom-uk-british-4084743/
    import English     from "./english.jpg";
    import German      from "./german.jpg";
    import {i18n}      from "../../../stores/i18n.js";
    import {language}  from "../../../stores/i18n.js";
</script>

<div id="container">
    <h1>{$i18n.AppShell.ChooseLanguage}</h1>

    <div id="inner">
        <a href="#/main" onclick={() => $language = "en"}>
            <img src={English} alt="{$i18n.AppShell.Language.en}">
        </a>
        <a href="#/main" onclick={() => $language = "de"}>
            <img src={German}  alt="{$i18n.AppShell.Language.de}">
        </a>
    </div>
</div>

<style>
    #container {
        flex: 1;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 2em;
    }

    #inner {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 4em;
    }

    img {
        display: block;
        max-width: 15em;
        transition: transform 0.5s, box-shadow 0.5s;
        cursor: pointer;
    }

    img:hover {
        transform: scale(110%) rotate(2deg);
        box-shadow: 5px 5px 10px rgba(0,0,0, 0.33);
    }
</style>