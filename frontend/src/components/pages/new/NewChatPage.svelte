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
Start view to choose the main UI language.
-->
<script lang="ts">
    // https://pixabay.com/illustrations/flag-of-germany-flag-german-flag-1060305/
    // https://pixabay.com/illustrations/flag-united-kingdom-uk-british-4084743/
    import English     from "./english.jpg";
    import German      from "./german.jpg";
    import {i18n}      from "../../../stores/i18n.js";
    import {language}  from "../../../stores/i18n.js";
    import {pageTitle} from "../../../stores/page.js";
    import {pageSubTitle} from "../../../stores/page.js";

    $pageTitle    = $i18n.AppShell.ChooseLanguage;
    $pageSubTitle = "";
</script>

<div id="container">
    <div id="flags">
        <a href="#/main" onclick={() => $language = "en"}>
            <img src={English} alt="{$i18n.AppShell.Language.en}" style="animation-delay: -0.1s">
        </a>
        <a href="#/main" onclick={() => $language = "de"}>
            <img src={German}  alt="{$i18n.AppShell.Language.de}" style="animation-delay: -0.5s">
        </a>
    </div>

    <div class="ui-message">
        {@html $i18n.AppShell.Introduction}
    </div>
</div>

<style>
    #container {
        flex: 1;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 6em;

        #flags {
            display: flex;
            flex-direction: row;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 4em;
        }
    }

    img {
        display: block;
        max-width: 15em;
        transition: max-width 0.25s, margin 0.25s;
        cursor: pointer;

        animation: spinning 1s ease-in-out alternate infinite;
    }

    img:hover {
        max-width: 16.5em;
        margin: -1.5em;
    }

    @keyframes spinning {
        0% {
            transform: rotate3d(1,2,0.25, -15deg);
            box-shadow: -2px -2px 4px rgba(0,0,0, 0.33);
        }

        100% {
            transform: rotate3d(1,2,0.25, 10deg);
            box-shadow: 2px 2px 4px rgba(0,0,0, 0.33);
        }
    }
</style>