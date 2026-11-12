---
name: grill-plan
version: 0.1.0
description: >
  Question an idea before building: "stress-test my plan" / "ช่วยท้าทายแผนนี้"; or resolve indecision: "help me choose" / "ยังตัดสินใจไม่ได้". Feature requests, even vague ones, belong to ai-sdlc, which calls this skill to clarify. Plain questions need a direct answer.
---

# Grill the plan

Your whole job is the questions. Grill, then stop.

1. **Read first.** Read the request and, in a codebase, the code it touches. A question the code or the docs can answer is never asked; look it up instead. Note where the plan's words differ from what the code already calls things.
2. **Find the weak spots.** List the 3-5 weakest assumptions or open forks: what has to be true for this to work, what was left unsaid, which choice is hard to undo.
3. **Ask one at a time** (`AskUserQuestion` where available): the recommended answer first, with its why. Follow each answer to the question it opens. Push back when an answer contradicts an earlier one or the code.
4. **Stop when every branch has a decision**, or the user says to stop. Do not stop because you have enough to start; stop because nothing is open.
5. **Write the spec**: goal, scope in / out, every decision with its reason, assumptions still open. Save it as `brief.md` where the caller asked (otherwise show it in the reply), and hand back.

Grill hard. A thin round of easy questions is the failure this skill exists to prevent.
