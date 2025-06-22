import * as esbuild from "esbuild";

import sveltePlugin from "esbuild-svelte";

let ctx = await esbuild.context({
    entryPoints: [`src/index.ts`],
    outdir: "static/_bundle/",

    bundle: true,
    splitting: true,
    sourcemap: true,
    format: "esm",

    mainFields: ["svelte", "browser", "module", "main"],
    conditions: ["svelte", "browser"],

    plugins: [sveltePlugin()],

    loader: {
        ".svg": "text",
        ".ttf": "dataurl",
        ".woff": "dataurl",
        ".woff2": "dataurl",
        ".eot": "dataurl",
        ".jpg": "dataurl",
        ".png": "dataurl",
        ".gif": "dataurl",
    }
});

let { host, port } = await ctx.serve({
    servedir: "static",
    port: 8888,
});

console.log(`Listening on ${host}:${port}`);