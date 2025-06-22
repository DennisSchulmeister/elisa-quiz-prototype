/*
 * Elisa: AI Learning Quiz
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type {I18N}        from "../i18n/index.js";

import {fallbackLanguage} from "../i18n/index.js";
import {defaultLanguage}  from "../i18n/index.js";
import {writable}         from "svelte/store";
import {readable}         from "svelte/store";
import {get}              from "svelte/store";

export {languages}        from "../i18n/index.js";
export {defaultLanguage}  from "../i18n/index.js";
export {fallbackLanguage} from "../i18n/index.js";

let setTranslations: (value: I18N) => void;
let customLanguages: any = {};

const _i18n = readable(await createTranslations(defaultLanguage), function(set) {
    setTranslations = set;
});

const _language = writable(defaultLanguage);

_language.subscribe(async function(newLanguage: string) {
    if (!setTranslations) return;
    setTranslations(await createTranslations(newLanguage));
});

/**
 * Message catalogue with all translations of the currently active language.
 * This is just a deeply structured key/value object, that can be directly
 * accessed with `$i18n.someKey` in the UI components.
 */
export const i18n = {
    subscribe: _i18n.subscribe,

    get value() {
        return get(_i18n);
    }
}

/**
 * Currently active language.
 */
export const language = {
    subscribe: _language.subscribe,
    set:       _language.set,
    update:    _language.update,

    get value() {
        return get(_language);
    },

    set value(value) {
        _language.set(value);
    },
};


/**
 * Utility function to replace placeholders in the form of `$key$` in the given
 * text with the property of the object given in the second parameter.
 * 
 * @param text Original text
 * @param values Key/values to insert
 * @return Text with replaced placeholders
 */
export function _(text: string, values: any): string {
    for (let key of Object.keys(values) || []) {
        text = text.replaceAll(`\$${key}\$`, values[key]);
    }

    return text;
}

/**
 * Utility function for study book authors to translate the application
 * into a custom language.
 * 
 * @param language 
 * @param translations 
 */
export function addCustomLanguage(language: string, translations: I18N) {
    customLanguages[language] = translations;
}

/**
 * Create a new message catalogue from the given langauge and the fallback language.
 * 
 * @param newLanguage Language code
 * @returns New message catalogue
 */
async function createTranslations(newLanguage: string): Promise<I18N> {
    let i18n = await import(`../i18n/lang/${fallbackLanguage}.ts`);
    let translations = deepCopy({}, i18n.default);

    if (newLanguage !== fallbackLanguage) {
        let i18n = await import(`../i18n/lang/${newLanguage}.ts`);
        deepCopy(translations, i18n.default);
    }

    if (newLanguage in customLanguages) {
        deepCopy(translations, customLanguages[newLanguage]);
    }

    return translations;
}

/**
 * Deep copy of an object with translatable texts, similar to `Object.assign()`.
 * Note that the object properties must be strings or nested translation objects.
 * If a property is an object, the function will copy its content by recursively
 * calling itself. All other values are copied via a simple assignment.
 * 
 * Properties of the target object that are missing in the source object remain
 * unmodified.
 * 
 * @param target Target object
 * @param source Source object
 * @returns Target object
 */
function deepCopy(target: any, source: any): any {
    for (let key of Object.keys(source)) {
        let value = source[key];

        if (typeof value === "object") {
            target[key] = {};
            deepCopy(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }

    return target;
}