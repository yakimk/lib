from __future__ import annotations

from copy import deepcopy

from collections.abc import Collection
from pabutools.rules.budgetallocation import BudgetAllocation
from pabutools.election import Instance, Project, total_cost, AbstractApprovalProfile
from pabutools.tiebreaking import TieBreakingRule, lexico_tie_breaking


def optimal_cost_av(
    instance: Instance,
    profile: AbstractApprovalProfile,
    p_target: Project,
    initial_budget_allocation: Collection[Project] | None = None,
    tie_breaking: TieBreakingRule | None = None,
) -> int | None:

    """
    Compute the maximal cost that a target project p_target could have
    while still being selected by Greedy Approval Voting.
   """

    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking

    if initial_budget_allocation is None:
        allocation = BudgetAllocation()
    else:
        allocation = BudgetAllocation(initial_budget_allocation)
    current_cost = total_cost(allocation)

    remaining = [p for p in instance if p not in allocation]
    scores = {p: profile.approval_score(p) for p in remaining}

    ordered: list[Project] = []
    to_order = set(remaining)

    while to_order:
        max_score = max(scores[p] for p in to_order)
        tied = [p for p in to_order if scores[p] == max_score]
        ordered_ties = tie_breaking.order(instance, profile, tied)
        ordered.extend(ordered_ties)
        to_order.difference_update(tied)

    for project in ordered:
        if profile.approval_score(project) <= 0:
            continue
        if project == p_target:
            res = instance.budget_limit - current_cost
            return None if res <= 0 else res

        if current_cost + project.cost <= instance.budget_limit:
            current_cost += project.cost

    return None