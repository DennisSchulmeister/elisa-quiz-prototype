import ChatQuizPage from "./pages/chat-quiz/ChatQuizPage.svelte"
import NotFoundPage from "./pages/errors/NotFoundPage.svelte";

export default {
    "/": ChatQuizPage,
    "*": NotFoundPage,
};
