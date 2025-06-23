/*
 * Elisa: AI Learning Quiz
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import LanguagePage from "./pages/language/LanguagePage.svelte";
import ChatQuizPage from "./pages/chat-quiz/ChatQuizPage.svelte"
import NotFoundPage from "./pages/errors/NotFoundPage.svelte";

export default {
    "/":     LanguagePage,
    "/main": ChatQuizPage,
    "*":     NotFoundPage,
};
