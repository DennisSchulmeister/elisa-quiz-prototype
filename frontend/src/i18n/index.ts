import en from "./lang/en.js";

/**
 * Typing for message catalogues. This simply mirrors the dynamically inferred
 * type of the master language, so that TypeScript can issue a warning for missing
 * translations in the other languages.
 */
export type I18N = typeof en;

/**
 * All available languages. Note, that there must be a `.ts` file of the
 * same name in this directory which default exports a key/value object
 * with the translated texts.
 */
export const languages = ["en", "de"];

/**
 * Fallback language to use for missing translations in the currently
 * active language.
 */
export const fallbackLanguage = "en";

/**
 * Default language when no other language has been chosen.
 */
export const defaultLanguage = "en";