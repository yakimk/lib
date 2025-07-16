import pytest
from pabutools.election import Project, Instance, ApprovalBallot, ApprovalProfile
from pabutools.rules.mes.mes_rule import method_of_equal_shares
from pabutools.election import Cost_Sat
from pabutools import election

from src.add_complement.add_complement_mes import add_complement_mes


@pytest.fixture
def setup_election():
    p1 = Project("p1", 10)
    p2 = Project("p2", 10)
    p3 = Project("p3", 15)

    instance = Instance()
    instance.update([p1, p2, p3])
    instance.budget_limit = 30

    b1 = ApprovalBallot([p1, p2])
    b2 = ApprovalBallot([p1, p2, p3])
    b3 = ApprovalBallot([p1, p2])
    b5 = ApprovalBallot([p1, p2])
    b6 = ApprovalBallot([p3])
    profile = ApprovalProfile([b1, b2, b3, b5, b6])

    return instance, profile, p1, p2, p3


def test_project_initially_selected(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    outcome = method_of_equal_shares(instance, profile, sat_class=Cost_Sat, resoluteness=True)
    assert p2 in outcome


def test_add_complement_makes_project_lose(setup_election):
    instance, profile, p1, p2, p3 = setup_election

    ell = add_complement_mes(
        p2,
        instance,
        profile,
        step=1
    )

    # new_profile = deepcopy(profile)
    assert isinstance(ell, int)
    assert ell > 0

    profile.extend(ell * [ApprovalBallot([p1, p3])])

    print("ELL: ", ell)
    print(profile)
    outcome = method_of_equal_shares(instance, profile, sat_class=Cost_Sat, resoluteness=True)
    print(outcome)
    assert p2 not in outcome


def test_project_not_selected_returns_zero(setup_election):
    instance, profile, p1, p2, p3 = setup_election

    ell = add_complement_mes(p3, instance, profile, step=1)
    assert ell == 0

@pytest.mark.slow
def test_real_world_example():

    instance, profile = election.parse_pabulib("./tests/pabulib/poland_warszawa_2017_kolo.pb")
    step = 1000
    outcome = method_of_equal_shares(instance, profile, sat_class=Cost_Sat, analytics=True)
    p = outcome[0]
    assert isinstance(p, Project)
    ell = add_complement_mes(p, instance, profile, step=step)

    assert ell > 0

    other_projects = [proj for proj in instance if proj != p]
    ballot = ApprovalBallot(set(other_projects))

    ballots = (ell - step) * [ballot]
    profile.extend(ballots)

    outcome = method_of_equal_shares(instance, profile, sat_class=Cost_Sat, analytics=True)
    assert p in outcome

    profile.extend( step * [ballot])

    outcome = method_of_equal_shares(instance, profile, sat_class=Cost_Sat, analytics=True)
    assert p not in outcome

    return 