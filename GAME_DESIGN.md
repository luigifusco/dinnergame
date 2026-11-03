# Sideplot

**Small talk. Secret plans.**

Secret missions and quirks for a dinner or an evening at a bar.

## Concept

An informal social game played alongside dinner, drinks, or another gathering.
Players receive secret cards that subtly influence their conversations and
behavior, without replacing normal socializing with turns or public challenges.

The intended payoff is **delayed recognition**:

> "Wait - is that why you kept bringing up trains?"

A good card produces behavior that seems plausible once, becomes suspicious
through repetition, and is funny in retrospect.

## Card types

**Quirks** give players a specific, absurd premise to develop through recurring
behavior. Keep one through a round, creating a pattern that others may gradually
notice. At the shared reveal, vote for **best use of a quirk**.

**Missions** describe achievable objectives with identifiable completion
conditions. Players can quietly replace them after succeeding. Missions remain
unscored.

These two types benefit from different replacement rules.

Editable card definitions, print-ready PDFs, and printing instructions are
available in [README.md](README.md).

## Internal card families

Organize cards by the interaction they create, rather than a fictional setting.
These families help us write a varied deck; players do not receive a theme, and
theme labels never appear on their cards.

| Type | Family | Main mechanism | Examples |
|---|---|---|---|
| Quirk | Language | Apply a peculiar way of speaking or explaining things. | Contractually Obliged, Couples Therapy |
| Quirk | Perspectives | Interpret ordinary things through a specific, absurd model. | The Heist, Definitely Human |
| Quirk | Social habits | Change how requests, compliments, and rituals work. | The Middleman, Gone Too Soon |
| Quirk | Callbacks and fiction | Give a recurring fiction or relationship a history over the evening. | The Incident, The Guest of Honor |
| Quirk | Accomplices | Cast another player in your joke without telling them. | Our Little Secret, Business Partners |
| Mission | Say something | Lead someone toward a particular word or phrase without supplying it. | Forecast, The Scenic Detour |
| Mission | Stories and know-how | Draw out an anecdote, useful detail, or connection between guests. | Origin Story, The Useful Tip |
| Mission | Shared decisions | Get people to compare ideas, agree, or coordinate an action. | Holiday Committee, Musical Chairs |
| Mission | Small actions | Elicit a natural gesture or conversational action rather than a dare. | Counting On It, The Sound Effect |
| Mission | Callbacks and adoption | Get a phrase, idea, or recommendation to travel beyond its originator. | Return Ticket, It Has a Name |
| Mission | Corrections and reactions | Set up a mistake, imitation, or curious question. | Close Enough, Inside Voice |
| Mission | Props and surprises | Prepare an object for someone to discover, try, or play along with. | Under Wraps, Stop and Smell |

The current library has **36 quirks and 67 missions** across five quirk
families and seven mission families. Families need not contain equal numbers of
cards. Quirk definitions retain the `cards\running` storage folder; mission
definitions live under `cards\mission`. A family can be divided into further
files whenever useful.

### Keeping the families distinct

"Say something" is about eliciting words you have not supplied. "Callbacks and
adoption" is about someone taking up an idea you deliberately introduced. A
callback quirk asks you to sustain a reference; a mission callback finishes
when another person takes it up.

"Small actions" catches something a player does during conversation. "Props and
surprises" starts with an object you prepare or plant; "corrections and reactions"
starts with something you say or do to prompt a response.

Some cards overlap. File a card under its main payoff rather than duplicating it
in multiple families. Themes are authoring aids, not extra win conditions.

### Variety and pacing

Mix families rather than dealing a whole table only word-elicitation tasks.
Otherwise normal conversation can turn into an obvious guessing game.

Single-word or gesture missions can resolve in one conversational moment.
Two-person missions may need more opportunity; some callbacks also require a
topic change. These are pacing differences, not tested difficulty ratings.
Do not force all missions to finish at the same speed.

For quirks, pair a strange premise with a specific, repeatable action. Give the
player several ways into it and room for the joke to develop. Do not prescribe
a theatrical voice, a full character, or a quota of repetitions. Useful cues
are opportunities, not compulsory reactions with penalties for missing them.

For missions, pick an observable finish: a correction, a copied gesture, a
question, or a discovered card. Give missions a concrete hook rather than a
whole conversation to manage.
Leave room for different approaches, with at most a small anti-cheat restriction.
State the task directly, without advice about keeping it brief, natural, or
playful. Keep conditions that define the challenge; leave out general etiquette
and tone restrictions.

## Mission difficulty

Difficulty should come from finding a good approach, not deciphering the card
or waiting for a very specific accident. A quick win and a more demanding
mission can coexist in the same hand.

### Prompting baseline

**Conversational questions, hints, and demonstrations are allowed. A bare request
to perform the listed action does not count.** The conversational reason can be
a pretext: "What did the engine sound like?" can prompt a sound effect; "Make a
noise for me" on its own cannot.

For word-elicitation missions, do not supply the target word, request it, or turn
the exchange into a guessing game. Adoption missions are different: introducing
the phrase or nickname is part of the task.

A specific condition on a card still applies. For example, **Return Ticket**
requires a topic to come back without a reminder; that is its central challenge,
not a blanket rule for all conversations.

### What to tune

| Lever | What changes the challenge | Example in this revision |
|---|---|---|
| Player control | A usable cue versus a wholly unsolicited response. | **Counting On It** now permits contextual questions and demonstrations. |
| Target precision | A word with several conversational entry points versus a particular person's exact phrasing. | **Tomorrow's Lunch** targets "leftovers" rather than waiting for "that's a good question." |
| Participants | One response versus a chain of people who all need to contribute. | **Resident Expert** needs one player to teach, not a third person to ask a follow-up. |
| Timing | Uptake in the current conversation versus an independent return later. | **The Echo** no longer requires a new context; **Return Ticket** keeps the delayed challenge. |
| Commitment | A verbal response versus an action beyond agreement. | **The Recommendation Chain** now ends with a written or saved recommendation. |

Change one lever at a time. To make **The Echo** harder, test reuse after a topic
change; do not simultaneously require two people and forbid all prompting.
To ease **The Recommendation Chain**, test the second player expressing interest
instead of saving the recommendation.

**Setup cost is separate from difficulty.** A table map can be awkward during
dinner even if getting someone to mark it is easy. **Open to Offers** now starts
with a spoken price, not a handmade tag. Missing props or an unsuitable setting
are reasons to exchange a card, not evidence that it is a good hard mission.

**Belief needs an observable payoff.** **Voice Control** asks someone to try an
invented command; **Invisible Ink** asks them to hold a napkin up to the light.
Neither requires deciding whether someone secretly believed a claim.

### Working bands

These are hypotheses for choosing test hands, **not playtested ratings**. Card
families are not difficulty tiers, and difficulty labels are not printed.

| Band | Intended experience | Initial candidates |
|---|---|---|
| Starter | A clear cue and one immediate response. | Close Enough; Inside Voice; Made You Look; Origin Story; Tomorrow's Lunch |
| Standard | A deliberate setup, a well-chosen question, or a reaction to a convincing premise. | Forecast; Counting On It; Invisible Ink; Voice Control; Pass It On |
| Stretch | Delayed uptake, coordinated contributions, or getting another person to act on a recommendation. | Return Ticket; Your Example, Their Point; The Joint Story; The Recommendation Chain |

For a first mission playtest, pair a starter candidate with a standard candidate
alongside the quirk. Offer stretch missions later rather than giving
someone two slow missions at the start. The named cards are examples, not fixed
packs.

### Playtest and revise

At the reveal, record the card ID and wording revision, whether a usable
opportunity arose, what prompt was tried, roughly how many attempts it took,
whether it succeeded, and whether the attempt was worth revealing.

Keep **success**, **attempted but failed**, **no usable opportunity**, and
**not attempted despite an opportunity** separate. Also note early suspicion,
but do not turn it into a new failure rule.

Look for patterns across several tables before assigning firmer bands. If a
card stalls despite available opportunities, remove one dependency or give it a
clearer entry point. If it is trivial and has little comic payoff, strengthen the
outcome or remove it. If people cannot find opportunities, reconsider the setup
rather than labeling it difficult.

Try the revised wording with another group and keep the version identifiable.
Early sessions should find broken or dull cards, not produce precise win-rate
claims.

## Formats

| Format | Hand | Replacement |
|---|---|---|
| **One-card starter** | One quirk | Keep it for 45-60 minutes, then reveal and vote. |
| **Three-card version** | One quirk and two missions | Keep the quirk through the reveal and vote; quietly replace completed missions. |
| **Timed rounds** | One mission per person | Replace at a shared break, roughly every 20-30 minutes. |

### Recommended starting point

Start with the one-card version. Introduce the hybrid three-card version if
players want more activity. The quirk voting format needs at least three
players. Choose a natural break for the reveal before beginning.

Three simultaneous quirks could be difficult to remember and might turn
everyone into an exaggerated character. In the hybrid version, the two missions
are opportunities to choose between, not obligations to pursue simultaneously.

Avoid mandatory ten-minute changes: a conversation might only just be creating
the right opportunity. For a longer evening, repeat the round with fresh quirks
after a reveal rather than replacing them mid-performance.

## Basic play

1. Explain that secret tasks will be in play, then deal the chosen hand to each
   player. Keep card contents private unless a task calls for another player to
   find the card.
2. Continue the gathering normally. There are no turns, and nobody needs to
   perform continuously.
3. Use an honor system for mission completion. Keep completed cards face down for
   the reveal rather than announcing success.
4. In the three-card version, quietly draw a replacement mission after completing
   one, maintaining one quirk and two active missions.
5. At the agreed break, pause for guessing, a reveal, and the quirk podium.

Before play, players may exchange an unsuitable quirk. Keep the chosen quirk
through the reveal so everyone develops one performance for the round.
Missions may still be discreetly exchanged during play.

For missions, use the [prompting baseline](#prompting-baseline): the player must
find a conversational pretext, not simply request the listed action.

Paper, a pen, and napkins cover most prop missions. Exchange a mission if its
props aren't available. Retrieve any hidden card after it's found, or when the
game ends.

## Example quirk cards

Keep one for the round. Develop a recognizable pattern rather than performing
continuously; there is no required number of repetitions.

| Card | Secret instruction |
|---|---|
| **The Incident** | Choose a trivial event from tonight. Refer back to it as "the incident" and imply that nobody is ready to talk about it. |
| **The Guest of Honor** | Treat an object on the table as an important guest. Consult it, defend its tastes, and include it in decisions. |
| **Contractually Obliged** | Add spoken fine print to your own offers, promises, and compliments, as if someone might sue you. |
| **Low-Budget Foley** | Supply sound effects for ordinary actions at the table. Give recurring actions their own signature sound. |
| **The Middleman** | Route requests and messages through another player, even when the intended recipient is sitting next to you. |
| **Gone Too Soon** | Deliver eulogies for finished dishes, empty glasses, and topics the conversation has abandoned. |
| **Fuck, Marry, Kill** | Keep proposing rounds of "fuck, marry, kill" using things mentioned in conversation. |

## Example mission cards

Each mission has an identifiable completion condition. Completion does not
require public proof or an interruption.

| Card | Secret instruction |
|---|---|
| **Forecast** | Get another player to say "umbrella" without saying it yourself, asking for the word, or starting a guessing game. |
| **The Echo** | Introduce an unusual expression and get another player to use it in their own sentence. |
| **Resident Expert** | Get another player to give you a step-by-step explanation of a skill they have. |
| **Holiday Committee** | Get two other people to suggest details for an imaginary group holiday. |
| **Human Diagram** | Get someone to explain something using an object on the table. |
| **Pass It On** | Whisper a message to another player. Get them to pass it on to a third player. |
| **Close Enough** | Misquote a familiar saying and get another player to correct it. |
| **Inside Voice** | Whisper a question and get another player to whisper their answer. |
| **Under Wraps** | Hide this card inside a folded napkin. Get another player to unfold it and find the card. |
| **Stop and Smell** | Fold a paper flower and get another player to smell it. |
| **Voice Control** | Invent a voice command for an object on the table. Get another player to try it. |
| **Invisible Ink** | Claim a blank napkin has a hidden message. Get another player to hold it up to the light. |
| **Edible Lyrics** | Sing a familiar lyric with one word replaced by a food. Get another player to sing the correct version. |
| **Proof of Life** | Get another player to take your pulse and tap the beat on the table. |
| **In Loving Memory** | Get another player to invent an epitaph for your gravestone. |

The curiosity-focused additions use new tasks and wording inspired by public
[Don't Get Got previews](https://bigpotato.co.uk/products/dont-get-got) and
[hands-on reviews](https://rolltoreview.com/dont-get-got-susd-edition-review/).
The useful mechanisms are planted irregularities, unusual favors, and
corrections with an observable payoff. For example, **Proof of Life** turns a
physical check into a tapped rhythm, while **Edible Lyrics** turns a correction
into a sung response. Avoid tasks whose main challenge is stalling the evening
or repeatedly asking for the same response.

## Discovery and reveal

Save formal guessing for a short reveal at a natural break, rather than allowing
continuous accusations or interrogation.

Make guesses before anyone reveals a quirk; guessing earns no points. Then
everyone shows their cards and can briefly recall one example of their quirk
in action. Others can add moments they noticed. Share mission attempts and
successes too, but do not use them to score the quirk performance.

The reveal is a shared recollection, not a campaign speech. Judge what happened
during the round, not a new performance after the cards have been shown.

Being suspected does not mean immediate failure. The dawning realization is part
of the fun, and recognition should be a payoff rather than a punishment.

## Scoring: the quirk podium

Vote for **best use of a quirk**, not simply the funniest person.

> Who made the most of their quirk through a clever interpretation, funny
> moments, or a satisfying reveal?

Judge the performance relative to the assigned card. Following its premise
matters; so do an inventive interpretation and a pattern that becomes funny
in retrospect. Quiet performances can win. Frequency, volume, and unrelated
jokes are not automatic reasons to award points.

These are considerations for one ballot, not separate numerical categories.
There is no minimum number of laughs or repetitions, and no scoring during
conversation.

1. After all quirks have been revealed, vote privately on paper.
2. Award **2 points** to your favorite performance and **1 point** to your
   second favorite. Name two different other players; no self-votes.
3. Add the votes and announce the first, second, and third places.

Equal totals share a place, with the next place skipped. For example, two joint
firsts are followed by third place. Everyone whose rank is first, second, or
third is on the podium, so ties can produce more than three names. There is no
tiebreaker performance or extra vote.

Scores apply only to quirks in this round. Mission completions, correct
guesses, and previous rounds do not add to the total. The mission-only timed
format has no quirk podium.

The format needs at least three players. No app, voting cards, repetition
counters, or referee is needed. Voting is subjective and may favor outgoing
players or easier cards; the podium is a celebratory ending, not a precise
measure of skill.

## Interactions between cards

The most promising cards interact without depending on each other.

For example, someone playing **Holiday Committee** starts planning an imaginary
holiday. **The Heist** turns the trip into an operation with roles and a getaway.
**The Committee** introduces an imaginary member who objects to the plan.

Likewise, a nickname introduced for **It Has a Name** might become a recurring
reference for **The Guest of Honor**, while **Old Enemy** develops a grudge
against that same object. The cards do not need to name or depend on one another
for these interactions to emerge, and combinations do not earn bonus points.

Each person thinks they are quietly recruiting the others into their joke, and
they all are.
