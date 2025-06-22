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
Root component of the application. Contains the background image and a router
to display the actual content based on the current URL.
-->
<script lang="ts">
    import Router            from 'svelte-spa-router'
    import ApplicationHeader from './ApplicationHeader.svelte';
    import routes            from "../routes.js";
</script>

<div id="app">
    <ApplicationHeader/>
    
    <main>
        <Router {routes} />
    </main>
</div>

<style>
    #app {
        /* https://pixabay.com/illustrations/learning-hint-school-subject-4264032/ */
        background-image: url(./background.png);
        background-size: cover;
        background-position: center;

        flex: 1;
        display: flex;
        flex-direction: column;
    }

    main {
        flex: 1;
        display: flex;
        flex-direction: column;

        overflow-y: auto;
        padding: 1rem;
    }
</style>