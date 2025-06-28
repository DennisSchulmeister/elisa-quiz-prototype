/*
 * Elisa: AI Learning Assistant
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
        ChooseLanguage: "Sprache wählen",

        Language: {
            en: "Englisch",
            de: "Deutsch",
        },

        Introduction: `
            <p>
                <b>ELISA</b> ist <i><u>dein persönlicher KI-Lernassistent</u></i>. Sie unterstützt dich dabei, neue Themen
                zu verstehen, dein Wissen zu vertiefen und ganz entspannt zu lernen – wann und wie es dir am besten passt.
                Ob Fragen beantworten, Zusammenhänge erklären oder spielerisch mit Lernquizzen arbeiten: ELISA ist für dich da.
            </p>
            <p>
                Aktuell befindet sich ELISA noch in der frühen Entwicklung. Damit sie noch besser wird, brauchen wir
                deine Unterstützung! Probiere ELISA einfach aus und nimm dir danach kurz Zeit für unsere Umfrage.
                Dein Feedback ist für uns enorm wertvoll – und fließt direkt in die Weiterentwicklung ein.
            </p>
            <p>&nbsp;</p>
            <p>
                <b>Hinweis:</b> Deine Chats werden nur in deinem Browser gespeichert. Bitte gebe dennoch keine sensiblen
                Daten ein.
            </p>
        `,
    },

    Chat: {
        MobileShowQuiz: "Zeige Quiz",
        Placeholder:    "Schreibe etwas …",
        TooltipSend:    "Nachricht abschicken",
        Disclaimer:     "KI kann eigenartige Fehler machen. Sei gewarnt. 🥸",
        Waiting:        "Warte …",
        ConnectionLost: "Verbindung unterbrochen. Versuche, die Verbindung wiederherzustellen.",

        ResetHistory: {
            MenuEntry: "Gesprächsverlauf zurücksetzen",
            Message:   "Bist du sicher, dass du den gesamten Nachrichtenverlauf löschen und zurücksetzen willst? Dadurch wird eine neue Sitzung gestartet und die Erinnerung von ELISA an vergangene Unterhaltungen zurückgesetzt.",
            Yes:       "Ja",
            No:        "Nein",
        },
    },

    Quiz: {
        MobileShowChat:      "Zeige Chat",
        QuestionNumber:      "Frage $1:",
        FeedbackCorrect:     "Das ist richtig!",
        FeedbackWrong:       "Leider falsch …",
        PromptFinalFeedback: "Dies sind meine Antwort. Bitte gib mir Feedback und erkläre es mir, wenn ich etwas falsch beantwortet habe:",
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