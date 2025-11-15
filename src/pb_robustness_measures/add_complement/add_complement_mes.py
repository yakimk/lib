from pabutools.election import Cost_Sat, ApprovalBallot
from copy import deepcopy
from pabutools.rules.mes.mes_rule import method_of_equal_shares


def add_complement_mes(project, instance, profile, step = 10, max_iter = 100,  verbose=False):
    new_profile = deepcopy(profile)
    new_instance = deepcopy(instance)
    other_projects = [p for p in instance if p != project]
    print(other_projects)
    ballot = ApprovalBallot(set(other_projects))
    ballots = step * [ballot]

    ell = 0

    for _ in range(max_iter):

        if ell > 0: new_profile.extend(ballots)

        outcome = method_of_equal_shares(new_instance, new_profile, sat_class=Cost_Sat, resoluteness=True)

        if project not in outcome:
            if verbose:
                if ell > 0:
                    print(f"Project {project.name} selected even after adding {ell-1} voters that approve only of its rivals.")
                else:
                    print(f"Project {project.name} is not selected in the first place.")

            return max(ell, 0)
        ell += step

    if verbose:
        print(f"Project {project.name} selected even after adding {step * max_iter} voters that approve of its rivals.")
    return None