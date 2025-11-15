from __future__ import annotations
from collections.abc import Collection
from copy import deepcopy

from pabutools.rules.budgetallocation import BudgetAllocation
from pabutools.utils import Numeric

from pabutools.fractions import frac
from pabutools.rules.phragmen import PhragmenVoter
from pabutools.election import (
    Instance,
    Project,
    AbstractApprovalProfile,
)
from pabutools.tiebreaking import TieBreakingRule, lexico_tie_breaking


def optimal_cost_sequential_phragmen(
    instance: Instance,
    profile: AbstractApprovalProfile,
    p_target: Project,
    initial_loads: list[Numeric] | None = None,
    initial_budget_allocation: Collection[Project] | None = None,
    tie_breaking: TieBreakingRule | None = None,
) -> Numeric:
    """
    Compute the optimal-cost for p_target under sequential Phragmen.
   """

    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking

    if initial_budget_allocation is None:
        initial_allocation = BudgetAllocation()
    else:
        initial_allocation = BudgetAllocation(initial_budget_allocation)

    cost_so_far = sum(proj.cost for proj in initial_allocation)

    if initial_loads is None:
        voters = [PhragmenVoter(b, 0, profile.multiplicity(b)) for b in profile]
    else:
        voters = [
            PhragmenVoter(b, initial_loads[i], profile.multiplicity(b))
            for i, b in enumerate(profile)
        ]

    orig_cost = p_target.cost
    p_target.cost = float("inf")

    try:
        all_projects = set(p for p in instance)
        current_pool = {
            p
            for p in all_projects
            if (p not in initial_allocation) and (p.cost <= instance.budget_limit)
        }

        supporters: dict[Project, list[int]] = {
            proj: [i for i, v in enumerate(voters) if proj in v.ballot]
            for proj in current_pool.union({p_target})
        }
        approval_scores: dict[Project, int] = {
            proj: profile.approval_score(proj) for proj in instance
        }

        s_p = approval_scores.get(p_target, 0)
        if s_p == 0:
            return 0

        def compute_new_maxload(j: Project) -> Numeric:
            sc = approval_scores[j]
            if sc == 0:
                return float("inf")
            total_load = sum(voters[i].total_load() for i in supporters[j])
            return frac(total_load + j.cost, sc)

        def sum_loads_of_target_supporters() -> Numeric:
            return sum(voters[i].total_load() for i in supporters[p_target])

        thresholds: list[Numeric] = []

        # MAIN LOOP: run phragmen on everything except p_target
        while True:
            feasible_projects = [
                j
                for j in current_pool
                if (approval_scores[j] > 0)
                and (cost_so_far + j.cost <= instance.budget_limit)
            ]
            if not feasible_projects:
                break

            new_loads = {j: compute_new_maxload(j) for j in feasible_projects}
            m_r = min(new_loads.values())  
            W_r = [j for j, nl in new_loads.items() if nl == m_r]

            S_r = sum_loads_of_target_supporters()
            raw_c_r = s_p * m_r - S_r
            B_r = instance.budget_limit - cost_so_far
            t_r = raw_c_r if raw_c_r <= B_r else B_r
            thresholds.append(t_r)

            chosen = tie_breaking.order(instance, profile, W_r)[0]

            for i_idx in supporters[chosen]:
                voters[i_idx].load = m_r

            cost_so_far += chosen.cost
            current_pool.remove(chosen)

        if not thresholds:
            return 0
        return max(max(thresholds), instance.budget_limit - cost_so_far)

    finally:
        p_target.cost = orig_cost
