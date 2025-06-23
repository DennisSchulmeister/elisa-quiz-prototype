/**
 * Fix TypeScript error for image imports. These are already handled by
 * esbuild, but we need to tell TypeScript, too.
 */
declare module "*.png" {
    const value: string;
    export default value;
}

declare module "*.jpg" {
    const value: string;
    export default value;
}

declare module "*.svg" {
    const value: string;
    export default value;
}