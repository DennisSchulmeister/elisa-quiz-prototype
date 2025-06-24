/*
 * Elisa: AI Learning Quiz
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

// This is the master language. Therefor no type import here.
export default {
    AppShell: {
        Title: "ELISA: AI Learning Quiz",
        ChooseLanguage: "Choose Language",

        Language: {
            en: "English",
            de: "German",
        }
    },

    Chat: {
        MobileShowQuiz: "Return to Quiz",
        Placeholder:    "Type something …",
        TooltipSend:    "Send Message",
        Disclaimer:     "AI can make silly mistakes. You have been warned. 🥸",
        Waiting:        "Waiting …",
    },

    Quiz: {
        MobileShowChat:      "Show Chat",
        QuestionNumber:      "Question $1:",
        FeedbackCorrect:     "That is correct!",
        FeedbackWrong:       "Sadly wrong …",
        PromptFinalFeedback: "These are my answers. Please give me feedback and explain to me, if I answered something wrong:",
    },

    WebsocketError: {
        FetchURL:           "Failed to fetch websocket URL.",
        NotConnected:       "No connection to the backend. Error code: $code$",
        UnknownError:       "An unknown error occurred while communicating with the backend.",
        UnknownMessageCode: "Unrecognized message code: $code$",
    },

    Error404: {
        TriggerLink: "Trigger 404 Page",
        Title:       "Page not found",
        Message1:    "We are terribly sorry, but the requested page <b>$url$</b> cannot be found.",
        Message2:    'Maybe go back to the <a href="#/">home page</a> and grab some other cheese, instead?',
    },
};