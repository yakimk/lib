from __future__ import annotations

from copy import copy, deepcopy
from collections.abc import Iterable

from pabutools.rules.budgetallocation import BudgetAllocation
from pabutools.rules.mes.mes_details import (
    MESAllocationDetails,
    MESIteration,
    MESProjectDetails,
)
from pabutools.utils import Numeric

from pabutools.election import AbstractApprovalProfile
from pabutools.election.satisfaction.satisfactionmeasure import GroupSatisfactionMeasure
from pabutools.election.ballot.ballot import AbstractBallot
from pabutools.election.instance import Instance, Project
from pabutools.election.profile import AbstractProfile
from pabutools.election.satisfaction import SatisfactionMeasure
from pabutools.tiebreaking import TieBreakingRule, lexico_tie_breaking
from pabutools.fractions import frac
from pabutools.rules.mes.mes_rule import MESProject, MESVoter, affordability_poor_rich, naive_mes



def mes_inner_algo(
    instance: Instance,
    profile: AbstractProfile,
    voters: list[MESVoter],
    projects: set[MESProject],
    tie_breaking_rule: TieBreakingRule,
    current_alloc: BudgetAllocation,
    all_allocs: list[BudgetAllocation],
    resoluteness: bool,
    skipped_project: MESProject | None = None,
    analytics: bool = False,
    verbose: bool = False,
) -> None:
    tied_projects: list[MESProject] = []
    if analytics:
        current_iteration = MESIteration()
        current_iteration.extend(
            [MESProjectDetails(p, current_iteration) for p in projects]
        )
        current_iteration.voters_budget = [voter.budget for voter in voters]
    best_afford = float("inf")
    if verbose:
        print("========================")
    for project in sorted(projects, key=lambda p: p.affordability):
        if verbose:
            print(f"\tConsidering: {project}")
        available_budget = sum(
            voters[i].total_budget() for i in project.supporter_indices
        )
        if available_budget < project.cost:  # unaffordable, can delete
            if verbose:
                print(
                    f"\t\t Removed for lack of budget: "
                    f"{float(available_budget)} < {float(project.cost)}"
                )
            projects.remove(project)
            if analytics:
                current_iteration.update_project_details_as_discarded(project)
            continue
        if (
            project.affordability > best_afford
        ):  # best possible afford for this round isn't good enough
            if verbose:
                print(
                    f"\t\t Skipped as affordability is too high: {float(project.affordability)} > {float(best_afford)}"
                )
            break
        project.supporter_indices.sort(
            key=lambda i: voters[i].budget_over_sat_project(project)
        )
        current_contribution = 0
        denominator = project.total_sat
        for i in project.supporter_indices:
            supporter = voters[i]
            afford_factor = frac(project.cost - current_contribution, denominator)
            if verbose:
                print(
                    f"\t\t\t {project.cost} - {current_contribution} / {denominator} = {afford_factor} * "
                    f"{project.supporters_sat(supporter)} ?? {supporter.budget}"
                )
            if afford_factor * project.supporters_sat(supporter) <= supporter.budget:
                # found the best afford_factor for this project
                project.affordability = afford_factor
                if analytics:
                    current_iteration.update_project_details_as_effective_vote_count_reduced(
                        project
                    )
                if verbose:
                    eff_vote_count = frac(
                        denominator, project.cost - current_contribution
                    )
                    print(
                        f"\t\tFactor: {float(afford_factor)} = ({float(project.cost)} - {float(current_contribution)})/{float(denominator)}"
                    )
                    print(f"\t\tEff: {float(eff_vote_count)}")
                if afford_factor < best_afford:
                    best_afford = afford_factor
                    tied_projects = [project]
                elif afford_factor == best_afford:
                    tied_projects.append(project)
                break
            current_contribution += supporter.total_budget()
            denominator -= supporter.multiplicity * project.supporters_sat(supporter)
    if verbose:
        print(f"{tied_projects}")
    if not tied_projects:
        if analytics and skipped_project:
            cover = sum(voters[i].budget for i in skipped_project.supporter_indices)
            new_eff = int(cover / skipped_project.cost * 100)
            current_alloc.details.skipped_project_eff_support = max(
                new_eff, current_alloc.details.skipped_project_eff_support
            )
        if analytics:
            current_alloc.details.iterations.append(current_iteration)
        if resoluteness:
            all_allocs.append(current_alloc)
        else:
            current_alloc.sort()
            if current_alloc not in all_allocs:
                all_allocs.append(current_alloc)
    else:
        if len(tied_projects) > 1:
            tied_projects = tie_breaking_rule.order(instance, profile, tied_projects)
            if resoluteness:
                tied_projects = tied_projects[:1]
        for selected_project in tied_projects:
            if resoluteness:
                new_alloc = current_alloc
                new_projects = projects
                new_voters = voters
            else:
                new_alloc = deepcopy(current_alloc)
                new_projects = deepcopy(projects)
                new_voters = deepcopy(voters)
            new_alloc.append(selected_project.project)
            new_projects.remove(selected_project)
            if verbose:
                print(
                    f"Price is {best_afford * selected_project.supporters_sat(selected_project.supporter_indices[0])}"
                )
            for i in selected_project.supporter_indices:
                supporter = new_voters[i]
                supporter.budget -= min(
                    supporter.budget,
                    best_afford * selected_project.supporters_sat(supporter),
                )
            if analytics and current_iteration:
                current_iteration.selected_project = selected_project
                current_iteration.voters_budget_after_selection = [
                    voter.budget for voter in new_voters
                ]
                current_alloc.details.iterations.append(current_iteration)
                current_iteration = None  # to avoid double appending
                if skipped_project:
                    cover = 0
                    for i in skipped_project.supporter_indices:
                        cover += min(
                            voters[i].budget,
                            best_afford * skipped_project.supporters_sat(voters[i]),
                        )
                    new_eff = int(cover / skipped_project.cost * 100)
                    current_alloc.details.skipped_project_eff_support = max(
                        new_eff, current_alloc.details.skipped_project_eff_support
                    )
            mes_inner_algo(
                instance,
                profile,
                new_voters,
                new_projects,
                tie_breaking_rule,
                new_alloc,
                all_allocs,
                resoluteness,
                skipped_project,
                analytics,
                verbose=verbose,
            )


def method_of_equal_shares_scheme(
    instance: Instance,
    profile: AbstractProfile,
    p_target,
    sat_profile: GroupSatisfactionMeasure,
    initial_budget_per_voter: Numeric,
    initial_budget_allocation: BudgetAllocation,
    tie_breaking: TieBreakingRule,
    resoluteness=True,
    voter_budget_increment=None,
    binary_sat=False,
    skipped_project: Project | None = None,
    analytics: bool = False,
    verbose: bool = False,
) -> BudgetAllocation | list[BudgetAllocation]:

    if verbose:
        print(f"Initial budget per voter is: {initial_budget_per_voter}")
    voters = []
    for index, sat in enumerate(sat_profile):
        voters.append(
            MESVoter(
                index,
                sat.ballot,
                sat,
                initial_budget_per_voter,
                sat_profile.multiplicity(sat),
            )
        )
        index += 1

    projects = set()
    for p in instance.difference(set(initial_budget_allocation)):
        mes_p = MESProject(p)
        total_sat = 0
        for i, v in enumerate(voters):
            indiv_sat = v.sat.sat_project(p)
            if indiv_sat > 0:
                total_sat += v.total_sat_project(p)
                mes_p.supporter_indices.append(i)
                if binary_sat:
                    mes_p.unique_sat_supporter = indiv_sat
                else:
                    mes_p.sat_supporter_map[v] = indiv_sat
        if total_sat > 0:
            if p.cost > 0:
                mes_p.total_sat = total_sat
                afford = frac(p.cost, total_sat)
                mes_p.initial_affordability = afford
                mes_p.affordability = afford
                projects.add(mes_p)
            else:
                initial_budget_allocation.append(p)

    budget_allocation = BudgetAllocation(
        initial_budget_allocation,
        (
            MESAllocationDetails([voter.multiplicity for voter in voters])
            if analytics
            else None
        ),
    )

    skipped_mes_project = None
    if skipped_project:
        skipped_mes_project = next(
            p for p in projects if p.name == skipped_project.name
        )
        projects = [p for p in projects if p.name != skipped_project.name]
        budget_allocation.details.skipped_project_eff_support = 0

    previous_outcome: BudgetAllocation | list[BudgetAllocation] = budget_allocation

    while True:
        all_budget_allocations: list[BudgetAllocation] = []
        mes_inner_algo(
            instance,
            profile,
            voters,
            copy(projects),
            tie_breaking,
            deepcopy(budget_allocation),
            all_budget_allocations,
            resoluteness,
            skipped_mes_project,
            analytics,
            verbose,
        )
        if resoluteness:
            outcome = all_budget_allocations[0]
            if voter_budget_increment is None:
                return outcome
            if not instance.is_feasible(outcome):
                return previous_outcome
            if instance.is_exhaustive(outcome, available_projects=projects):
                return outcome
            initial_budget_per_voter += voter_budget_increment
            previous_outcome = outcome
        else:
            if voter_budget_increment is None:
                return all_budget_allocations
            if any(not instance.is_feasible(o) for o in all_budget_allocations):
                return previous_outcome
            if any(
                instance.is_exhaustive(o, available_projects=projects)
                for o in all_budget_allocations
            ):
                return all_budget_allocations
            initial_budget_per_voter += voter_budget_increment
            previous_outcome = all_budget_allocations
        for voter in voters:
            voter.budget = initial_budget_per_voter
        for p in projects:
            p.affordability = p.initial_affordability


def optimal_cost_mes(
    instance: Instance,
    profile: AbstractProfile,
    p_target: Project,
    sat_class: type[SatisfactionMeasure] | None = None,
    sat_profile: GroupSatisfactionMeasure | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
    initial_budget_allocation: Iterable[Project] | None = None,
    voter_budget_increment=None,
    binary_sat=None,
    skipped_project: Project | None = None,
    analytics: bool = False,
    verbose: bool = False,
) -> BudgetAllocation | list[BudgetAllocation]:
    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking
    if initial_budget_allocation is not None:
        budget_allocation = BudgetAllocation(initial_budget_allocation)
    else:
        budget_allocation = BudgetAllocation()
    if sat_class is None:
        if sat_profile is None:
            raise ValueError("sat_class and sat_profile cannot both be None")
    else:
        if sat_profile is None:
            sat_profile = profile.as_sat_profile(sat_class=sat_class)

    if binary_sat is None:
        binary_sat = isinstance(profile, AbstractApprovalProfile)

    return method_of_equal_shares_scheme(
        instance,
        profile,
        p_target,
        sat_profile,
        frac(instance.budget_limit, profile.num_ballots()),
        budget_allocation,
        tie_breaking,
        resoluteness=resoluteness,
        voter_budget_increment=voter_budget_increment,
        binary_sat=binary_sat,
        skipped_project=skipped_project,
        analytics=analytics,
        verbose=verbose,
    )
