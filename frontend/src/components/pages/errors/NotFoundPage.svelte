<!--
@component
Simple 404 not found page
 -->
<script lang="ts">
    import {i18n, _}  from "../../../stores/i18n.js";
    import {location} from 'svelte-spa-router'
</script>

<div>
    <h1>{$i18n.Error404.Title}</h1>
    <p>
        {@html _($i18n.Error404.Message1, {url: $location})}
    </p>
    <p>
        {@html $i18n.Error404.Message2}
    </p>
    <img src="page-not-found.png" alt="">
</div>

<style>
    div {
        flex: 1;
        align-self: center;
    }

    img {
        display: block;
        width: 30em;
        max-width: 100%;
        margin-top: 3em;
    }
</style>
