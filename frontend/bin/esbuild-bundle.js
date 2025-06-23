import * as esbuild from "esbuild";
import sveltePlugin from "esbuild-svelte";

esbuild.build({
    entryPoints: [`src/index.ts`],
    outdir: "static/_bundle/",    

    bundle: true,
    splitting: true,
    minify: true,
    sourcemap: true,
    format: "esm",

    mainFields: ["svelte", "browser", "module", "main"],
    conditions: ["svelte", "browser"],

    plugins: [sveltePlugin()],
    
    loader: {
        ".svg": "dataurl",
        ".ttf": "dataurl",
        ".woff": "dataurl",
        ".woff2": "dataurl",
        ".eot": "dataurl",
        ".jpg": "dataurl",
        ".png": "dataurl",
        ".gif": "dataurl",
    },
});
