import pytest
from copy import deepcopy
from pabutools.election import Project, Instance, ApprovalBallot, ApprovalProfile, total_cost
from pabutools import election
from src.rules.greedyAV import greedy_av


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
    b4 = ApprovalBallot([p1, p2])
    b5 = ApprovalBallot([p3])
    profile = ApprovalProfile([b1, b2, b3, b4, b5])

    return instance, profile, p1, p2, p3


def test_initial_greedy_selection(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    outcome = greedy_av(instance, profile)
    assert p1 in outcome
    assert p2 in outcome
    assert p3 not in outcome
    assert total_cost(outcome) <= instance.budget_limit


def test_priority_change_with_extra_p3_approvals(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    extra = 3
    profile.extend(extra * [ApprovalBallot([p3])])

    outcome = greedy_av(instance, profile)
    assert p3 in outcome
    assert p1 in outcome
    assert p2 not in outcome
    assert total_cost(outcome) <= instance.budget_limit


def test_with_initial_allocation(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    initial = [p3]
    outcome = greedy_av(instance, profile, initial_budget_allocation=initial)
    assert p3 in outcome
    assert p1 in outcome
    assert p2 not in outcome
    assert total_cost(outcome) <= instance.budget_limit


def test_no_affordable_projects(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    instance.budget_limit = 5
    outcome = greedy_av(instance, profile)
    assert len(outcome) == 0


def test_full_selection_when_affordable(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    instance.budget_limit = 50
    outcome = greedy_av(instance, profile)
    assert set(outcome) == {p1, p2, p3}


@pytest.mark.slow
def test_real_world_instance():
    path = "./tests/pabulib/poland_warszawa_2017_kolo.pb"
    instance, profile = election.parse_pabulib(path)
    outcome = greedy_av(instance, profile)
    assert total_cost(outcome) <= instance.budget_limit
    for proj in outcome:
        assert proj in instance