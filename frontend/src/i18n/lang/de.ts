/*
 * Elisa: AI Learning Quiz
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type {I18N} from "../index.js";

const i18n: I18N = {
    AppShell: {
        Title: "ELISA: KI-Lernquiz",
    },

    Chat: {
        MobileShowQuiz: "Zurück zum Quiz",
        Disclaimer: "KI kann ziemlich doofe Fehler machen. Sei gewarnt. 🥸",
    },

    Quiz: {
        MobileShowChat: "Zeige Chat",
    },

    WebsocketError: {
        FetchURL:           "Fehler beim Abrufen der Websocket URL.",
        NotConnected:       "Keine Verbindung mit dem Backend. Fehlercode: $code$",
        UnknownError:       "Während der Kommunikation mit dem Backend ist ein unbekannter Fehler aufgetreten.",
        UnknownMessageCode: "Unbekannter Nachrichtencode: $code$",
    },

    Error404: {
        TriggerLink: "404 Seite auslösen",
        Title:       "Seite nicht gefunden",
        Message1:    "Es tut uns fürchterlich Leid, aber die angeforderte Seite <b>$url$</b> wurde nicht gefunden.",
        Message2:    'Wollen Sie stattdessen zur <a href="#/">Startseite</a> zurückgehen und sich einen anderen Käse schnappen?',
    },
};

export default i18n;