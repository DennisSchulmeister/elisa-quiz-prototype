/*
 * Elisa: AI Learning Quiz
 * © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type { Writable }     from "svelte/store";
import { writable }          from "svelte/store";
import { _, i18n, language } from "./i18n.js";
import QuizStore             from "./quiz.js";

/**
 * Websocket message exchanged between frontend and backend. This is deliberately
 * kept simple. It simply contains a message code with additional data.
 */
interface WebSocketMessage {
    code?: string;
    [key: string]: any;
};

/**
 A single chat message to be displayed in the UI.
 */
export interface ChatMessage extends WebSocketMessage {
    id?:   string;
    role?: "user" | "agent" | "error";
    text?: string;
};

/**
 * Error message received from the backend
 */
export interface ErrorMessage extends WebSocketMessage {
    text?: string;
}

/**
 * A reactive WebSocket store that manages a connection to the backend server
 * and synchronizes chat messages between the client and server.
 */
export class ChatStore {
    /**
     * Sevelte store which holds all chat messages
     */
    private store: Writable<ChatMessage[]> = writable([]);
    subscribe = this.store.subscribe;

    /**
     * Websocket connection to the backend
     */
    private socket!: WebSocket;

    /**
     * Flag that we are connected with the backend.
     */
    connected = false;

    /**
     * Dummy method to prevent "variable declared but never used" when we first
     * import the chat store to connect with the backend as early as possible.
     */
    noop() {
    }

    /**
     * Establish the WebSocket connection using the URL fetched from the backend.
     */
    async connect() {
        try {
            const response = await fetch("/api.url");
            const wsUrl = (await response.text()).trim() + "/ws/chat";

            this.socket = new WebSocket(wsUrl);
            this.socket.addEventListener("message", this.handleMessage.bind(this));
            this.socket.addEventListener("error", this.handleError.bind(this));

            // Send initial message to trigger greeting from LLM
            this.socket.addEventListener("open", () => {
                this.connected = true;
                this.send("chat_input", {text: "Hi!", language: language.value});
            });

            this.socket.addEventListener("close", () => this.connected = false);
        } catch (error) {
            let errorMessage = error instanceof Error ? error.message : String(error);
            this.appendError(i18n.value.WebsocketError.FetchURL + " " + errorMessage);
        }
    }

    /**
     * Append a user message to the message store and send it to the backend, which
     * should cause the backend to stream back a chat replies.
     * 
     * @param text - Message text
     */
    sendChatMessage(text: string, hidden: boolean = false) {
        const chatMessage: ChatMessage = {
            code:     "chat_input",
            id:       crypto.randomUUID(),
            role:     "user",
            text:     text,
            language: language.value,
        };

        if (!hidden) {
            this.store.update((messages) => [...messages, chatMessage]);
        }
        
        this.send("chat_input", {text: text, language: language.value});
    }

    /**
     * Internal method to send a message to the backend. The message will be JSON encoded
     * and shaped according to the `WebSocketMessage` type. If the socket is not open, an
     * error message is added to the store.
     *
     * @param code - Message type
     * @param data - Message data
     */
    private send(code: string, data: Record<string, any> = {}) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ code, ...data });
            this.socket.send(message);
        } else {
            this.appendError(_(i18n.value.WebsocketError.NotConnected, {code}));
        }
    }

    /**
     * Handle incoming Websocket message and dispatch it to the appropriate handler method
     * based on the message code.
     */
    private handleMessage = (event: MessageEvent) => {
        try {
            const message: WebSocketMessage = JSON.parse(event.data);

            const handler = `handle_${message.code}`;
            const func    = (this as any)[handler];

            if (typeof func === "function") {
                func.call(this, message);
            } else {
                this.appendError(_(i18n.value.WebsocketError.UnknownMessageCode, {"code": message.code}));
            }
        } catch (err) {
            console.error(err);
            this.appendError(err instanceof Error ? err.message : String(err));
        }
    };

    /**
     * Handle 'chat_reply' message from the server by inserting or updating
     * the corresponding agent message in the chat store.
     * 
     * @param inboundMessage - Received websocket message
     */
    private handle_chat_reply(inboundMessage: WebSocketMessage) {
        const chatMessage: ChatMessage = {
            code: "chat_reply",
            id:   inboundMessage.id,
            role: "agent",
            text: inboundMessage.text,
        };

        this.store.update((messages) => {
            const index = messages.findIndex((m) => m.id === chatMessage.id);

            if (index !== -1) {
                return [
                    ...messages.slice(0, index),
                    { ...messages[index], text: chatMessage.text },
                    ...messages.slice(index + 1),
                ];
            } else {
                return [...messages, chatMessage];
            }
        });
    }

    /**
     * Handle 'quiz' message from the server by updating the quiz stores respectively.
     * @param inboundMessage - Received websocket message
     */
    private handle_quiz(inboundMessage: WebSocketMessage) {
        let quizData = inboundMessage.data;
        
        if (quizData) {
            QuizStore.updateFromBackend(quizData);
        }
    }

    /**
     * Handle 'error' message from the server by displaying it in the chat window.
     * @param inboundMessage - Received websocket message
     */
    private handle_error(inboundMessage: ErrorMessage) {
        this.appendError(inboundMessage.text || i18n.value.WebsocketError.UnknownError);
    }

    /**
     * Handle a general websocket error like connection timeout etc. This simply
     * append an error message to the chat messages.
     */
    private handleError(error: Event): void {
        const errorText = (error instanceof Error && error.message) ? error.message : i18n.value.WebsocketError.UnknownError;
        this.appendError(errorText);
    }

    /**
     * Append error message to the chat message store.
     * @param text - Error text
     */
    private appendError(text: string) {
        const errorMessage: ChatMessage = {
            code: "error",
            id:   crypto.randomUUID(),
            role: "error",
            text: text,
        };

        this.store.update((messages) => [...messages, errorMessage]);
    }
}

export const chat = new ChatStore();
QuizStore.setChat(chat);