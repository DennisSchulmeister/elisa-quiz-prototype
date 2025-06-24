<!--
Elisa: AI Learning Quiz
© 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
-->

<!--
@component
Main container for the quiz game.
-->
<script lang="ts">
    import QuizStore     from "../../../stores/quiz.js";
    import {i18n}        from "../../../stores/i18n.js";
    import AnswerCorrect from "./quiz-answer-correct.png";
    import AnswerWrong   from "./quiz-answer-wrong.png";

    let feedback: ""|"correct"|"wrong" = $state("");

    function onAnswerClicked(event: MouseEvent, answer: number) {
        event.preventDefault();
        if (!$QuizStore.currentQuestion) return;

        feedback = QuizStore.answer(answer) ? "correct" : "wrong";

        window.setTimeout(() => {
            QuizStore.goon();
            feedback = "";
        }, 3000);
    }
</script>

<div id="container">
    {#if feedback === ""}
        <div id="question">
            <div class="number">
                {$i18n.Quiz.QuestionNumber.replace("$1", $QuizStore.currentQuestion?.number?.toString() || "")}
            </div>
            <div class="text">
                {$QuizStore.currentQuestion?.question || ""}
            </div>
        </div>

        <ol id="answers">
            {#each $QuizStore.currentQuestion?.answers || [] as answer, index}
                <li>
                <a
                        href         = "#answer"
                        class:color1 = {index % 4 == 0}
                        class:color2 = {index % 4 == 1}
                        class:color3 = {index % 4 == 2}
                        class:color4 = {index % 4 == 3}
                        onclick      = {event => onAnswerClicked(event, index)}
                    >
                        <span class="number">{index + 1}</span>
                        <span class="text">{answer}</span>
                    </a>
                </li>
            {/each}
        </ol>
    {:else if feedback === "correct"}
        <div id="feedback" class="correct">
            <img src={AnswerCorrect} alt="">
            <div>
                {$i18n.Quiz.FeedbackCorrect}
            </div>
        </div>
    {:else if feedback === "wrong"}
        <div id="feedback" class="wrong">
            <img src={AnswerWrong} alt="">
            <div>
                {$i18n.Quiz.FeedbackWrong}
            </div>
        </div>
    {/if}
</div>

<style>
    #container {
        flex: 1;

        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        gap: 2em;

        box-sizing: border-box;
        min-height: 100%;
        max-height: 100%;
        overflow-y: auto;

        font-size: 150%;

        backdrop-filter: blur(3px);
        padding: 1em;
        border: 1px solid rgba(0,0,0, 0.05);
        border-radius: 0.5rem;
    }

    #question {
        font-weight: bold;
        font-size: 130%;
        color: darkslateblue;

        .number {
            font-size: 75%;
            text-align: center;
            color: rgb(45, 20, 103);
        }
    }

    #answers {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 1em;

        list-style: none;

        li {
            margin: 0;
            padding: 0;
            width: calc(50% - 1em);
        }
            
        a {
            display: block;
            width: 100%;
            height: 100%;
            text-align: start;

            box-sizing: border-box;
            padding: 0.5em;
            border-radius: 0.5rem;

            color: white;
            cursor: pointer;

            transition: color 0.25s, box-shadow 0.25s, transform 0.25s;

            &:hover {
                box-shadow: 2px 2px 6px rgba(0,0,0, 0.33);
            }

            .number {
                font-weight: bold;
                margin-right: 0.5em;
            }
        }

        .color1 {
            background-color: hsl(353, 80%, 50%);

            .number {
                color: hsl(353, 80%, 80%);
            }

            &:hover {
                transform: scale(105%) rotate(2deg);
            }
        }

        .color2 {
            background-color: hsl(200, 80%, 50%);

            .number {
                color: hsl(200, 80%, 80%);
            }

            &:hover {
                transform: scale(105%) rotate(-3deg);
            }
        }

        .color3 {
            background-color: hsl(45, 80%, 50%);

            .number {
                color: hsl(45, 80%, 80%);
            }

            &:hover {
                transform: scale(105%) rotate(-1.75deg);
            }
        }

        .color4 {
            background-color: hsl(100, 60%, 50%);

            .number {
                color: hsl(100, 60%, 80%);
            }

            &:hover {
                transform: scale(105%) rotate(2.5deg);
            }
        }
    }

    #feedback {
        flex: 1;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2em;

        font-weight: bold;
        font-size: 150%;

        img {
            display: block;
            width: 100%;
            max-width: 10em;
            animation: feedback-image 1.5s ease-in-out alternate infinite;
        }

        div {
            text-align: center;
            text-shadow: 1px 1px black;
            animation: feedback-text 0.9s ease-in-out alternate infinite;
        }
        
        &.correct {
            color: hsl(40, 75%, 45%);
        }

        &.wrong {
            color: hsl(0, 70%, 50%);
        }
    }

    @keyframes feedback-image {
        0% {
            transform: rotate3d(0,0,0, 0deg);
        }

        100% {
            transform: rotate3d(0,1,0, 360deg);
        }
    }

    @keyframes feedback-text {
        0% {
            transform: rotate(-3deg);
        }

        100% {
            transform: rotate(4.5deg);
        }
    }

    @media all and (width < 700px) {
        #container {
            font-size: 130%;
        }

        #answers li {
            width: 100%;
        }
    }
</style>