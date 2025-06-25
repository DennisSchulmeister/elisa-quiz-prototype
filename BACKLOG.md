Development Backlog and Ideas
=============================

1. [Website](#website)
1. [Backend and AI](#backend-and-ai)
1. [User Management](#user-management)
1. [Teachers](#teachers)
1. [Additional Activities](#additional-activities)

Roughly, more important ideas first, since the following ones build upon them.

Website
-------

- [ ] Setup a small static website (using [Cactus](https://github.com/eudicots/Cactus))
- [ ] Put some documentation online

Backend and AI
--------------

- [ ] Split reasoning and text generation with the [ReAct pattern](https://arxiv.org/abs/2210.03629)
- [ ] Make quiz feedback a backend function (instead of sending a fake user message from the frontend)
- [ ] Allow the LLM to choose between different activities (not only Kahoot-style quizzes)

User Management
---------------

- [ ] Add database (probably [MongoDB](https://www.mongodb.com/))
- [ ] Add authentication and authorization features
- [ ] Add user feedback mechanism (small survey: 5-star rating, type of user, wanted features, comments)
- [ ] Rework "choose language" page in frontend to a small user sign-up workflow (choose avatar, language, your learning interests, …)
- [ ] Persist chat conversations, allow to revisit, continue and delete previous conversations

Teachers
--------

- [ ] Allow teachers to define lightweight curricula and learning paths
- [ ] Allow students to bookmark curricula and learning paths
- [ ] Allow students either free learning or following a pre-defined learning path

Additional Activities
---------------------

- [ ] Multi-user game mode, where a whole class is playing the same quiz
- [ ] Learning cards: AI gives a word, which the student must explain in own words
- [ ] Free-text exercises: AI gives an exercise description, student must describe the solution
- [ ] Gap text: Student must fill in gaps in an AI generated text
- [ ] Writing exercise: AI gives an text which the student must improve (spelling, grammar, style)