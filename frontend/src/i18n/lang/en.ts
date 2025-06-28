/*
 * Elisa: AI Learning Assistant
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
        Title: "Elisa: AI Learning Assistant",
        ChooseLanguage: "Choose Language",

        Language: {
            en: "English",
            de: "German",
        },

        Introduction: `
            <p>
                <b>ELISA</b> is <i><u>your personal AI learning assistant</u></i>. She helps you to understand new topics,
                deepen your knowledge and learn in a relaxed way–when and how it suits you best. Whether it's answering
                questions, explaining contexts or working playfully with learning quizzes: ELISA is there for you.
            </p>
            <p>
                ELISA is still in the early stages of development. To make her even better, we need your support!
                Simply try out ELISA and then take some time to complete our survey. Your feedback is extremely
                valuable to us–and will flow directly into further development.
            </p>
            <p>&nbsp;</p>
            <p>
                <b>Note:</b> Your chats are only saved in your browser. However, please do not enter any sensitive data.
            </p>
        `,
    },

    Chat: {
        MobileShowQuiz: "Show Quiz",
        Placeholder:    "Type something …",
        TooltipSend:    "Send Message",
        Disclaimer:     "AI can make silly mistakes. You have been warned. 🥸",
        Waiting:        "Waiting …",
        ConnectionLost: "Connection lost. Trying to reconnect.",

        ResetHistory: {
            MenuEntry: "Reset Message History",
            Message:   "Are you sure that you want to clear and reset the whole message history? This will start a new session and reset ELISA's memory of past conversations.",
            Yes:       "Yes",
            No:        "No",
        },
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