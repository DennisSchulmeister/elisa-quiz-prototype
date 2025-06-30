/*
 * Elisa: AI Learning Assistant
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
 * Connection status to adapt the UI accordingly. Initially it will always be
 * "disconnected" and the main UI will remain invisible. Once the connection
 * becomes available it will be "connected". If the connection goes down after
 * that it will be "connection-lost". We periodically try to (re)connect after
 * a small waiting time while the connection is down.
 */
export type ConnectionStatus = "disconnected" | "connected" | "connection-lost";

/**
 * Websocket message exchanged between frontend and backend. This is deliberately
 * kept simple. It simply contains a message code with additional data.
 */
interface WebSocketMessage {
    code?: string;
    [key: string]: any;
};

/**
 * Origin of the message
 */
export type MessageRole = "user" | "agent" | "error" | "status";

/**
 * Whether the message contains normal text content (speak) or intermediate
 * reasoning steps (think)
 */
export type MessageType = "say" | "think";

/**
 A single chat message to be displayed in the UI.
 */
export interface ChatMessage extends WebSocketMessage {
    id?:   string;
    role?: MessageRole;
    type?: MessageType;
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
     * Connection status
     */
    connectionStatus: ConnectionStatus = "disconnected";

    /**
     * Constructor. Tries to reconstruct the previous chat messages.
     */
    constructor() {
        this.restoreMessages();
    }

    /**
     * Dummy method to prevent "variable declared but never used" when we first
     * import the chat store to connect with the backend as early as possible.
     */
    noop() {
    }

    /**
     * Establish the WebSocket connection using the URL fetched from the backend.
     * @param reset - Reset history and start new session
     */
    async connect(resetHistory: boolean = false) {
        try {
            // Reset chat history
            if (resetHistory) {
                return this.store.update(messages => this.saveMessages([]));
            }

            // Establish connection
            const response = await fetch("/api.url");
            const wsUrl = (await response.text()).trim();

            this.socket = new WebSocket(wsUrl);
            this.socket.addEventListener("message", this.handleMessage.bind(this));
            this.socket.addEventListener("error", this.handleError.bind(this));

            // Send initial message to trigger greeting from LLM
            this.socket.addEventListener("open", () => {
                this.connectionStatus = "connected";
                this.send("chat_input", {text: "Hi!", language: language.value});
            });

            this.socket.addEventListener("close", () => {
                // Show status message
                console.error(i18n.value.Chat.ConnectionLost);
                this.appendMessage("status", "say", i18n.value.Chat.ConnectionLost);

                // Try to reconnect
                this.connectionStatus = "connection-lost";
                window.setTimeout(this.connect, 5000);
            });
        } catch (error) {
            // Show error message
            this.connectionStatus = "disconnected";

            console.error(error);
            let errorMessage = error instanceof Error ? error.message : String(error);
            this.appendMessage("error", "say", i18n.value.WebsocketError.FetchURL + " " + errorMessage);

            // Try to reconnect
            window.setTimeout(this.connect, 10000);
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
            this.store.update(messages => this.saveMessages([...messages, chatMessage]));
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
            this.appendMessage("error", "say", _(i18n.value.WebsocketError.NotConnected, {code}));
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
                this.appendMessage("error", "say", _(i18n.value.WebsocketError.UnknownMessageCode, {"code": message.code}));
            }
        } catch (err) {
            console.error(err);
            this.appendMessage("error", "say", err instanceof Error ? err.message : String(err));
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
                return this.saveMessages([
                    ...messages.slice(0, index),
                    { ...messages[index], text: chatMessage.text },
                    ...messages.slice(index + 1),
                ]);
            } else {
                return this.saveMessages([...messages, chatMessage]);
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
        this.appendMessage("error", "say", inboundMessage.text || i18n.value.WebsocketError.UnknownError);
    }

    /**
     * Handle a general websocket error like connection timeout etc. This simply
     * append an error message to the chat messages.
     */
    private handleError(error: Event): void {
        const errorText = (error instanceof Error && error.message) ? error.message : i18n.value.WebsocketError.UnknownError;
        this.appendMessage("error", "say", errorText);
    }

    /**
     * Append new message to the chat message store.
     * 
     * @param role - Message role
     * @param type - Message type
     * @param text - Message text
     */
    private appendMessage(role: MessageRole, type: MessageType, text: string) {
        const errorMessage: ChatMessage = {
            code: "chat",
            id:   crypto.randomUUID(),
            role: role,
            type: type,
            text: text,
        };

        this.store.update(messages => this.saveMessages([...messages, errorMessage]));
    }

    /**
     * Persist updated chat messages in the local storage, so that it can be restored
     * after an accidental page reload.
     * 
     * @param messages Current chat messages
     * @returns Saved messages
     */
    private saveMessages(messages: ChatMessage[]): ChatMessage[] {
        localStorage.setItem("chatMessages", JSON.stringify(messages));
        return messages;
    }

    /**
     * Restore chat messages from local storage. This overwrites all previously
     * contained messages in the store object!
     */
    private restoreMessages() {
        this.store.update(_ => {
            return JSON.parse(localStorage.getItem("chatMessages") || "[]");
        });
    }
}

export const chat = new ChatStore();
QuizStore.setChat(chat);