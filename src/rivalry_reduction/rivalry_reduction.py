import random
from copy import deepcopy
from pabutools.election import Instance, AbstractApprovalProfile, Project

def rivalry_reduction(
    instance: Instance,
    profile: AbstractApprovalProfile,
    target: Project,
    voting_rule,
    trials: int = 100,
    step: int = 1,
    tie_breaking=None,
    sat_class = None,
) -> int | None:
    """
    Compute the Rivalry-Reduction measure for PB rule.
    Depending on whether `target` initially wins or loses we compute the average 
    number of voters that have to be persuaded to vote only for `target`'s opponents 
    or non-supporters that will approve of `target` only.
   """
    supporters = [i for i, ballot in enumerate(profile) if target in ballot]
    if not supporters:
        return None
    if sat_class:
        initial_alloc = voting_rule(instance, profile, tie_breaking=tie_breaking, sat_class = sat_class)
    else:
        initial_alloc = voting_rule(instance, profile, tie_breaking=tie_breaking)

    initially_wins = target in initial_alloc
    all_projects = [p for p in instance]

    total_supporters = len(supporters)
    for l in range(0, total_supporters + 1, step):
        successes = 0
        for _ in range(trials):
            chosen = set(random.sample(supporters, l))
            profile_mod = deepcopy(profile)
            for idx in chosen:
                if initially_wins:
                    new_approvals = [p for p in all_projects if p != target]
                else:
                    new_approvals = [target]
                profile_mod[idx] = type(profile_mod[idx])(new_approvals)
            if sat_class:
                alloc = voting_rule(instance, profile_mod, tie_breaking=tie_breaking, sat_class = sat_class)
            else:
                alloc = voting_rule(instance, profile_mod, tie_breaking=tie_breaking)
            wins = target in alloc
            if wins:
                successes += 1
        
        if initially_wins:
            if successes < (trials + 1) // 2:
                return -(l - 1)
        else:
            if successes >= (trials + 1) // 2:
                return l

    return None
