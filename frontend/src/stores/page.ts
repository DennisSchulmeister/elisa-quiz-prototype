/*
 * Elisa: AI Learning Quiz
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import { writable } from "svelte/store";

/**
 * Main title of the current page or quiz.
 */
export const pageTitle = writable("");

/**
 * Sub-title of the current page or quiz.
 */
export const pageSubTitle = writable("");