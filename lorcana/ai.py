"""The AI player.

:class:`SearchAI` plans a whole turn at a time:

1. Clone the game, hiding what it shouldn't know (the opponent's hand and both
   deck orders are re-randomised).
2. Beam-search sequences of main-phase actions, ranking partial plans by a static
   evaluation of the resulting position.
3. For the most promising complete plans, simulate the opponent's reply turn with
   the heuristic policy and score the position that comes out of it.  This is what
   stops the AI from questing into lethal challenges or over-extending.
4. Play the winning plan, replanning if the real game diverges from the plan.
"""

from __future__ import annotations

from .actions import (ActivateAction, ChallengeAction, InkAction, PassAction,
                      PlayAction, QuestAction, ShiftAction, SingAction)
from .controllers import Controller, HeuristicController
from .evaluate import DEFAULT_WEIGHTS, WIN_SCORE, evaluate


def state_signature(game, index):
    """A hashable summary of the position, used to drop duplicate search nodes."""
    me = game.players[index]
    them = game.players[1 - index]
    parts = [me.lore, them.lore, me.available_ink, me.total_ink,
             tuple(sorted(card.id for card in me.hand))]
    for player in (me, them):
        parts.append(tuple(sorted(
            (c.card.id, c.ready, c.drying, c.damage, c.strength_mod,
             c.cant_quest, c.cant_challenge,
             tuple(sorted(c.extra_keywords)), tuple(sorted(c.pending_flags)))
            for c in player.characters)))
        parts.append(tuple(sorted((i.card.id, i.ready) for i in player.items)))
        parts.append(len(player.discard))
    return tuple(parts)


class SearchAI(Controller):
    # Defaults are the strongest settings measured in paired self-play; they cost
    # roughly a quarter of a second per turn, which interactive play can afford.
    def __init__(self, name="AI", beam_width=28, max_depth=20, rollouts=24,
                 reply_weight=0.7, follow_up=True, samples=4, policy=None,
                 reply_policy=None, weights=DEFAULT_WEIGHTS):
        super().__init__(name)
        self.weights = weights
        self.beam_width = beam_width
        self.max_depth = max_depth
        self.rollouts = rollouts
        self.reply_weight = reply_weight
        # Guesses at the opponent's hidden cards per candidate plan.
        self.samples = samples
        # Also simulate our own next turn, so plans are judged on what we can
        # follow up with rather than on how the board looks the moment they end.
        self.follow_up = follow_up
        self.policy = policy or HeuristicController("ai-policy", weights=weights)
        # How the opponent is assumed to play during rollouts.  Defaults to the
        # same rule-based policy; a (shallow) SearchAI models a tougher opponent.
        self.reply_policy = reply_policy or self.policy
        self._plan = []
        self._plan_key = None
        self.nodes_searched = 0

    def reset(self):
        """Forget any cached plan (used between simulated turns)."""
        self._plan = []
        self._plan_key = None

    # -- controller interface ------------------------------------------

    def choose_action(self, game, player, actions):
        key = (game.turn_number, player.index)
        if self._plan_key != key:
            self._plan = self.plan_turn(game, player)
            self._plan_key = key
        replans = 0
        while self._plan:
            action = self._plan.pop(0)
            if action in actions:
                return action
            # The real game diverged from the simulation: plan again, but don't
            # get stuck replanning if the plan keeps coming back unusable.
            replans += 1
            if replans > 2:
                break
            self._plan = self.plan_turn(game, player)
        return PassAction() if PassAction() in actions else \
            self.policy.choose_action(game, player, actions)

    def choose(self, game, player, prompt, options, kind, intent=None,
               optional=False, labeler=None, meta=None):
        return self.policy.choose(game, player, prompt, options, kind=kind,
                                  intent=intent, optional=optional,
                                  labeler=labeler, meta=meta)

    # -- planning ------------------------------------------------------

    def plan_turn(self, game, player):
        index = player.index
        controllers = [self.policy, self.policy]
        root = game.clone_for_search(index, controllers=controllers)
        beam = [(root, [])]
        seen = {state_signature(root, index)}
        terminals = []          # (static score, plan, state)
        self.nodes_searched = 0

        for _depth in range(self.max_depth):
            successors = []
            for state, plan in beam:
                actions = state.legal_actions()
                for action in actions:
                    if isinstance(action, PassAction):
                        score = evaluate(state, index, self.weights)
                        terminals.append((score, plan, state))
                        continue
                    child = state.fast_clone(controllers=controllers)
                    child.apply(action)
                    self.nodes_searched += 1
                    signature = state_signature(child, index)
                    if signature in seen:
                        continue
                    seen.add(signature)
                    score = evaluate(child, index, self.weights)
                    if child.winner == index:
                        return plan + [action]
                    successors.append((score, plan + [action], child))
            if not successors:
                break
            successors.sort(key=lambda item: item[0], reverse=True)
            beam = [(state, plan) for _score, plan, state in
                    successors[: self.beam_width]]

        # Whatever plans are left in the beam are complete too (they ran out of
        # depth, or every follow-up was a duplicate).
        for state, plan in beam:
            terminals.append((evaluate(state, index, self.weights), plan, state))
        if not terminals:
            return []

        terminals.sort(key=lambda item: item[0], reverse=True)
        candidates = self.pick_candidates(terminals, index)
        best_plan, best_score = candidates[0][1], None
        for static_score, plan, state in candidates:
            score = self.score_with_reply(state, index, static_score)
            if best_score is None or score > best_score:
                best_plan, best_score = plan, score
        return list(best_plan)

    def pick_candidates(self, terminals, index):
        """The best distinct end-of-turn positions, ready for a rollout each.

        Grouping these by "kind of turn" to force variety was measurably worse
        than simply taking the best ones, so this stays a straight top-N.
        """
        candidates = []
        seen = set()
        for static_score, plan, state in terminals:
            signature = state_signature(state, index)
            if signature in seen:
                continue
            seen.add(signature)
            candidates.append((static_score, plan, state))
            if len(candidates) >= self.rollouts:
                break
        return candidates

    def score_with_reply(self, state, index, static_score):
        """Blend the position after our turn with the position after the reply.

        The reply is simulated against several guesses at the opponent's hand, so
        a plan is judged on how it holds up in general rather than against one
        lucky or unlucky sample.
        """
        if state.winner is not None:
            return WIN_SCORE if state.winner == index else -WIN_SCORE
        controllers = [None, None]
        controllers[index] = self.policy
        controllers[1 - index] = self.reply_policy
        total = 0.0
        for _ in range(self.samples):
            if hasattr(self.reply_policy, "reset"):
                self.reply_policy.reset()
            sim = state.fast_clone(controllers=controllers)
            sim.resample_hidden(index)
            sim.end_turn()
            sim.advance_turn()
            sim.play_turn()          # the opponent's reply
            if sim.winner is None and self.follow_up:
                sim.advance_turn()
                sim.play_turn()      # and what we could do with the turn after
            if sim.winner is not None:
                total += WIN_SCORE if sim.winner == index else -WIN_SCORE
            else:
                total += evaluate(sim, index, self.weights)
        reply_score = total / self.samples
        return (1.0 - self.reply_weight) * static_score + self.reply_weight * reply_score


class GreedyAI(HeuristicController):
    """The rule-based policy exposed as a stand-alone (weaker) opponent."""

    def __init__(self, name="Greedy"):
        super().__init__(name)
