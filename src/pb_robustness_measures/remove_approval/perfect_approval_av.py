from __future__ import annotations

from copy import deepcopy

from collections.abc import Collection
from pabutools.rules.budgetallocation import BudgetAllocation
from pabutools.election import Instance, Project, total_cost, AbstractApprovalProfile
from pabutools.tiebreaking import TieBreakingRule, lexico_tie_breaking


def perfect_approval_av(
    instance: Instance,
    profile: AbstractApprovalProfile,
    p_target: Project,
    initial_budget_allocation: Collection[Project] | None = None,
    tie_breaking: TieBreakingRule | None = None,
) -> int | None:
    """
    Returns the exact amount of voters that would have to approve of `p_target`
    for it to be selected.
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

    p_price = p_target.cost
    p_score = scores[p_target]
    p_ties = None

    while to_order:
        max_score = max(scores[p] for p in to_order)
        tied = [p for p in to_order if scores[p] == max_score]
        if max_score == p_score:
            p_ties = deepcopy(tied)

        ordered_ties = tie_breaking.order(instance, profile, tied)
        # if len(ordered_ties)>  1:
            # print("ASDIAJDA", ordered_ties, scores[ordered_ties[0]], scores[ordered_ties[0]])
        ordered.extend(ordered_ties)
        to_order.difference_update(tied)

    # print("START:", scores[p_target])
    best_so_far = None
    for project in ordered:
        if profile.approval_score(project) <= 0:
            continue

        if p_price + current_cost <= instance.budget_limit:
            best_so_far = scores[project]
            print(best_so_far)
        else:
            if len(p_ties) > 1:
                if tie_breaking.order(instance, profile, tied)[0] != p_target:
                    return best_so_far + 1

            return best_so_far

        if project == p_target:
            # print("now")
            continue

        if current_cost + project.cost <= instance.budget_limit:
            # allocation.append(project)
            current_cost += project.cost

    if p_price + current_cost <= instance.budget_limit:
        return 1

    if len(p_ties) > 1:
        if tie_breaking.order(instance, profile, tied)[0] != p_target:
            return best_so_far + 1

    return best_so_far