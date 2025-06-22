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