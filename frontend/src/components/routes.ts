/*
 * Elisa: AI Learning Assistant
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import LanguagePage     from "./pages/new/NewChatPage.svelte";
import MainPage         from "./pages/main/MainPage.svelte"
import ResetHistoryPage from "./pages/reset-history/ResetHistoryPage.svelte";
import NotFoundPage     from "./pages/errors/NotFoundPage.svelte";

export default {
    "/":              LanguagePage,
    "/main":          MainPage,
    "/reset-history": ResetHistoryPage,
    "*":              NotFoundPage,
};
