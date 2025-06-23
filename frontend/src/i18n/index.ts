/*
 * Elisa: AI Learning Quiz
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

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
export const defaultLanguage = localStorage.getItem("language") || "en";