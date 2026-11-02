# Sideplot V2: Quirks and the Podium

**Status: proposal for review.** The current rules, YAML cards, and printable
deck have not changed. The podium direction is agreed; the rules below and the
replacement quirk roster are the proposed implementation.

## What V2 changes

Quirks should give players a specific, absurd premise to develop over the
evening, with a reason to make it memorable. They should not just suggest a
manner of speaking or ask someone to supply their own entertainment.

V2 rewards **best use of a quirk** at the shared reveal. It does not award
points for repetitions or require the group to monitor each other's behavior.

- Keep one quirk for a round and develop it across ordinary conversations.
- Reveal the cards, recall what happened, and vote for the best performances.
- Replace vague quirks with more distinctive premises and recurring actions.
- Keep missions as separate, achievable objectives with their existing rules.

This replaces the proposed trigger-and-streak mechanic. There are no
three-success thresholds, resets for missed cues, or automatic quirk
replacements after a fixed number of actions. A card can suggest a useful
occasion without making every such occasion compulsory.

## Proposed round

The voting format needs at least three players.

Deal one quirk per player. For the hybrid format, also deal two missions and
replace completed missions as before. Allow an initial quirk exchange before
play, then keep the chosen quirk through the reveal. This is a deliberate
change from unrestricted quirk exchanges: each player develops one performance
for the round. Mission exchanges remain available.

Choose a natural break for the reveal, initially after about 45-60 minutes.
There are no turns or interruptions for scoring during the gathering.

Quirks stay secret, but being suspected or recognized is not failure. Players
do not need to announce every successful attempt, count repetitions, or
perform continuously. The podium rewards what actually happened during the
round, not a new performance delivered after the cards are revealed.

### Reveal and voting

1. Make guesses before anyone shows their quirk. Guessing earns no points.
2. Reveal all quirks. Each player can briefly recall one example; others can
   add moments they noticed. This is a shared recollection, not a campaign
   speech or a requirement to prove every action.
3. Vote privately, after seeing everyone's card. Give **2 points** to your
   favorite performance and **1 point** to your second favorite. These must be
   two different other players; no self-votes.
4. Add the votes and announce the podium.

Use one question:

> Who made the most of their quirk through a clever interpretation, funny
> moments, or a satisfying reveal?

Judge the performance **relative to the assigned card**. Actually following
its premise matters. A quiet recurring detail that suddenly makes sense can
beat a much louder performance. Frequency, volume, and an unrelated good joke
are not automatic reasons to award points.

These are considerations for one ballot, not separate numerical categories.
There is no minimum number of laughs or repetitions.

Equal totals share a place, with the next place skipped: two joint firsts are
followed by third place. Everyone whose rank is first, second, or third is on
the podium, so ties can produce more than three names. Do not add a tiebreaker
performance or another vote.

Votes score only the quirk performance in this round. Mission completions,
correct guesses, and previous rounds do not add to this total. Keep missions
unscored in V2 rather than inventing a conversion between completed objectives
and audience votes.

Paper ballots and a tally are enough. V2 does not need an app, a host judging
every exchange, or additional printed voting components.

## Making the quirks less vanilla

The target is **a strange internal logic**, not simply more emphatic wording.
A useful quirk makes a normal moment slightly wrong in a consistent way.

| Instead of | Give the player |
|---|---|
| "Be enthusiastic." | An absurd standard for what deserves admiration. |
| "Say unusual things." | A recurring belief or explanation they can apply to new situations. |
| "Invent a character." | A specific action: consult an object, issue a verdict, invent a product feature. |
| "Repeat a catchphrase." | Something that can acquire new meanings or a history during the round. |
| "Be funny." | A premise whose execution the group can recognize at the reveal. |

Keep the instruction concise and literal. One or two sentences should define
the behavior, not follow it with advice about being subtle, playful, or
convincing. Do not add scoring reminders or general etiquette caveats to cards.

The roster should mix verbal habits, interpretations, social interactions, and
object-based behavior. Not every card should ask for a speech, an invented
authority, or a theatrical voice. An evolving joke is useful, but a mandatory
three-scene script is not.

Players should have several ways into a quirk during an ordinary dinner or bar
conversation. Avoid cards that depend on a rare accidental phrase, special
preparation, or everyone agreeing to stop and play a separate game.

## Draft quirk roster

Keep **22 quirks** in the existing four authoring files. These are proposed
card texts, not extra rules. The current-to-V2 mapping makes replacements
explicit; there is no requirement to preserve a weak premise.

### Callbacks and fiction

File: `cards\running\callbacks-and-fiction.yaml`.

| Current card | V2 title | Proposed instruction |
|---|---|---|
| Previously, at This Table | The Incident | Choose a trivial event from tonight. Refer back to it as "the incident" and imply that nobody is ready to talk about it. |
| Tomorrow's Headline | Spoiler Alert | Treat other people's real-life stories as a TV series you've already seen. Drop hints about what happens next. |
| The Committee | The Committee | Refer decisions to an imaginary committee. Report its verdicts, including objections from one member who keeps causing problems. |
| A Useful Motto | Family Wisdom | Invent a family saying that makes no sense. Quote it as advice and explain it differently each time. |
| Unofficial Mascot | The Guest of Honor | Treat an object on the table as an important guest. Consult it, defend its tastes, and include it in decisions. |

### Language and verbal habits

File: `cards\running\language.yaml`.

| Current card | V2 title | Proposed instruction |
|---|---|---|
| Borrowed Wisdom | The Prophet | Choose another player as your personal oracle. Quote their earlier remarks as predictions of whatever happens next. |
| Infrastructure Enthusiast | More Roundabouts | Propose adding a roundabout as the solution to unrelated problems. |
| Quiet Footnotes | Contractually Obliged | Add spoken fine print to your own offers, promises, and compliments, as if someone might sue you. |
| Careful Conclusions | Known Issue | Describe your own mistakes as known issues. Announce updates and workarounds for your behavior. |
| Easily Impressed | World-Class | Praise routine actions as elite athletic performances, complete with technique analysis and comparisons to past champions. |
| Domestic Metaphors | Couples Therapy | Explain unrelated problems as relationship trouble between the things involved. |

### Perspectives

File: `cards\running\perspectives.yaml`.

| Current card | V2 title | Proposed instruction |
|---|---|---|
| The Logistics Department | The Heist | Discuss ordinary plans as heists. Assign roles, identify the target, and worry about the getaway. |
| The Unappointed Critic | The Unappointed Critic | Rate ordinary things using units you invent. Defend your scale as if everyone should already understand it. |
| Future Museum | Definitely Human | Ask practical questions about ordinary human habits, as if you learned about people from an unreliable manual. |
| Soundtrack Consultant | Low-Budget Foley | Supply sound effects for ordinary actions at the table. Give recurring actions their own signature sound. |
| Everything Is a Design Choice | Hidden Features | Give product demonstrations of ordinary objects, inventing features nobody needs. |

### Social habits and rituals

File: `cards\running\social-habits.yaml`.

| Current card | V2 title | Proposed instruction |
|---|---|---|
| Tiny Triumphs | Gone Too Soon | Deliver eulogies for finished dishes, empty glasses, and topics the conversation has abandoned. |
| Future Tradition | Ancient Tradition | Invent a ritual around something that happens tonight. Later, insist it's a tradition you've all followed for years. |
| The Specific Compliment | Suspiciously Specific | Compliment people on talents you've inferred from almost no evidence, then ask them for advice as the expert. |
| Quiet Fan Club | Old Enemy | Hold a grudge against an object on the table. Blame it for setbacks and object whenever someone praises it. |
| Bridge Maker | The Middleman | Route requests and messages through another player, even when the intended recipient is sitting next to you. |
| Fuck, Marry, Kill | Fuck, Marry, Kill | Keep proposing rounds of "fuck, marry, kill" using things mentioned in conversation. |

The last card is deliberately retained rather than padded with extra wording.
It already supplies a concrete, absurd recurring activity.

### Interactions to look for

Cards should work alone but become richer together:

- The Guest of Honor gives an object authority; Old Enemy can develop a grudge
  against the same object without either card requiring that pairing.
- The Heist turns an existing plan into an operation; The Committee can make
  getting approval absurdly difficult.
- The Prophet quotes an earlier remark; The Incident gives that remark a
  suspicious history.
- Gone Too Soon mourns an empty dish; Hidden Features can demonstrate its
  previously undisclosed second purpose.

These are examples, not required combinations or additional scoring bonuses.
Do not deliberately build every hand around them.

## What stays unchanged

- The 46 missions, their wording, contextual-prompting baseline, and provisional
  difficulty guidance.
- One quirk in the starter hand, or one quirk plus two missions in the hybrid.
- Internal type `running`, the `cards\running` folder, and `--kind running`.
- The existing YAML schema. Voting is a rule of play, not a new per-card field.
- Fronts showing only type, title, and instruction; the displayed type is QUIRK.
- The two wordless back designs and Balsamiq Sans typography.
- The 88 x 31.5 mm cards, sixteen per A4 sheet, and long-edge duplex layout.

The proposed library remains **68 cards: 22 quirks and 46 missions**. It should
still produce five front pages, five back pages, ten duplex pages, and twelve
unused positions on the last sheet.

## Implementation sequence

1. **Review this proposal.** Confirm the draft quirks and the voting details
   before replacing live cards.
2. **Update the quirk YAML files.** Keep IDs for refined premises; give genuine
   replacements descriptive `running-*` IDs. Preserve file counts and ordering
   within each type. Do not change mission definitions.
3. **Update the current rules and README.** Replace the old no-scoring section
   with the V2 reveal and podium rules. Update quirk examples, family
   descriptions, exchanges, and interaction examples to match the actual YAML.
   Keep the mission prompting and difficulty sections intact.
4. **Validate and regenerate the existing PDFs.** Use the existing fit check,
   Ruff checks, and PDF regression suite. Shorten wording before changing the
   compact layout or reducing the current 11 pt task text. Check the actual
   deck's labels, content, front/back pairing, and final empty positions.
5. **Publish the approved V2.** Verify that mission definitions and the
   wordless back PDF are unchanged, inspect a representative front sheet, and
   commit and push the source and regenerated PDFs. Mark this document as
   implemented and make the live rules the authority for play.

No renderer redesign, dependency additions, schema migration, or new scoring
software is planned.

## What a first playtest should tell us

The voting procedure and card roster are design hypotheses, not balanced or
playtested results.

Record which quirk each player held, a remembered moment, whether opportunities
were available, and what voters liked about the leading performances. Look for:

- Cards that produce one good joke but have nowhere to go afterward.
- Cards that require constant invention or never find an opening.
- Cards whose premise wins votes regardless of how the player used it.
- Voting that follows volume or popularity rather than use of the assigned
  quirk.
- Quiet performances that become satisfying only when the card is revealed.

Do not interpret a low vote total alone as proof that a card is too difficult
or a player performed badly. Compare the same card across different groups
before deciding whether its premise needs revision.
