import pytest

from pabutools.election import Project, Instance, ApprovalBallot, ApprovalProfile, total_cost
from src.optimal_cost.optimal_cost_av import optimal_cost_av
from src.rules.greedyAV import greedy_av

@pytest.fixture
def setup_election():
    p1 = Project("p1", 10)
    p2 = Project("p2", 20)
    p3 = Project("p3", 15)

    instance = Instance()
    instance.update([p1, p2, p3])
    instance.budget_limit = 30

    b1 = ApprovalBallot([p1, p2])
    b2 = ApprovalBallot([p1, p3])
    b3 = ApprovalBallot([p2])
    profile = ApprovalProfile([b1, b2, b3])

    return instance, profile, p1, p2, p3


def test_optimal_cost_for_selected_target(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    cost = optimal_cost_av(instance, profile, p1)
    assert isinstance(cost, int)
    assert cost == instance.budget_limit


def test_optimal_cost_for_late_target(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    cost = optimal_cost_av(instance, profile, p3)
    assert cost is None


def test_with_initial_allocation(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    initial = [p2]
    cost = optimal_cost_av(instance, profile, p1, initial_budget_allocation=initial)
    assert cost == instance.budget_limit - total_cost(initial)

@pytest.mark.slow
def test_real_world_target_in_selection(tmp_path):
    from pabutools import election
    path = "./tests/pabulib/poland_warszawa_2017_kolo.pb"
    instance, profile = election.parse_pabulib(path)
    alloc = greedy_av(instance, profile)
    target = alloc[0]
    cost = optimal_cost_av(instance, profile, target)
    assert cost is not None
    assert cost <= instance.budget_limit
