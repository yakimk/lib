import pytest
from pabutools.election import Project, Instance, ApprovalBallot, ApprovalProfile 
from src.rules.greedyAV import greedy_av
from src.rivalry_reduction.rivalry_reduction import rivalry_reduction
from pabutools.rules.phragmen import sequential_phragmen
from pabutools.rules.mes.mes_rule import method_of_equal_shares
from pabutools.election import Cost_Sat

@pytest.fixture
def simple_two_projects():
    p1 = Project("p1", 10)
    p2 = Project("p2", 10)
    p3 = Project("p3", 10)
    p4 = Project("p4", 10)
    p5 = Project("p5", 21)
    instance = Instance()
    ps = [p1, p2, p3, p4, p5]
    instance.update(ps)
    instance.budget_limit = 30

    b1 = ApprovalBallot([p1, p2])
    b2 = ApprovalBallot([p1, p2, p3])
    b3 = ApprovalBallot([p1, p2])
    b4 = ApprovalBallot([p1, p2])
    b5 = ApprovalBallot([p3])
    b6 = ApprovalBallot([p4])
    b7 = ApprovalBallot([p5])

    profile = ApprovalProfile([b1, b2, b3, b4, b5, b6, b7])
    return instance, profile, ps

def test_rivalry_reduction_losing_av(simple_two_projects):
    instance, profile, ps = simple_two_projects
    p3 = ps[1]
    result = rivalry_reduction(instance, profile, p3, greedy_av, trials=20)
    assert isinstance(result, int)
    assert -2 <= result <= 0

def test_rivalry_reduction_winning_av(simple_two_projects):
    instance, profile, ps = simple_two_projects
    p1 = ps[0]
    result = rivalry_reduction(instance, profile, p1, greedy_av, trials=20)
    assert isinstance(result, int)
    # assert result == 1

def test_no_supporters_returns_none_av(simple_two_projects):
    instance, profile, ps = simple_two_projects

    p6 = Project("p6", 5)
    instance.update([p6])
    result = rivalry_reduction(instance, profile, p6, greedy_av)
    assert result is None

@pytest.mark.slow
def test_realistic_scenario_av():
    from pabutools import election
    path = "./tests/pabulib/poland_warszawa_2017_kolo.pb"
    instance, profile = election.parse_pabulib(path)
    alloc = greedy_av(instance, profile)
    p3 = alloc[0]

    assert p3 in greedy_av(instance, profile)
    result = rivalry_reduction(instance, profile, p3, greedy_av, trials=5)
    assert result <= 0 


    for p in instance:
        if p not in alloc:
            p3 = p
            break
    # print(instance)
    # print(profile)

    assert p3 not in greedy_av(instance, profile)
    result = rivalry_reduction(instance, profile, p3, greedy_av, trials=5)

    assert result > 0 

    profile.extend([ApprovalBallot([p3])] * result)
    assert p3 in greedy_av(instance, profile)


def test_rivalry_reduction_losing_phragmen(simple_two_projects):
    instance, profile, ps = simple_two_projects
    p3 = ps[2]
    result = rivalry_reduction(instance, profile, p3, sequential_phragmen, trials=20)
    assert isinstance(result, int)
    assert -2 <= result <= 0

def test_rivalry_reduction_winning_phragmen(simple_two_projects):
    instance, profile, ps = simple_two_projects
    p1 = ps[0]
    result = rivalry_reduction(instance, profile, p1, sequential_phragmen, trials=20)
    assert isinstance(result, int)

def test_no_supporters_returns_none_phragmen(simple_two_projects):
    instance, profile, ps = simple_two_projects
    p6 = Project("p6", 5)
    instance.update([p6])
    result = rivalry_reduction(instance, profile, p6, sequential_phragmen)
    assert result is None

@pytest.mark.slow
def test_realistic_scenario_phragmen():
    from pabutools import election
    path = "./tests/pabulib/poland_warszawa_2017_kolo.pb"
    instance, profile = election.parse_pabulib(path)
    alloc = sequential_phragmen(instance, profile)
    p3 = alloc[0]
    result = rivalry_reduction(instance, profile, p3, sequential_phragmen, trials=5)
    assert result <= 0

    for p in instance:
        if p not in alloc:
            p3 = p
            break
    result = rivalry_reduction(instance, profile, p3, sequential_phragmen, trials=5)
    assert result > 0

    profile.extend([ApprovalBallot([p3])] * (result + 20)) # may potentially fail its probabilistic
    assert p3 in sequential_phragmen(instance, profile)

# def test_rivalry_reduction_losing_mes(simple_two_projects):
#     instance, profile, ps = simple_two_projects
#     p3 = ps[2]
#     result = rivalry_reduction(instance, profile, p3, method_of_equal_shares, trials=20, sat_class=Cost_Sat)
#     assert isinstance(result, int)
#     assert -2 <= result <= 0

def test_rivalry_reduction_winning_mes(simple_two_projects):
    instance, profile, ps = simple_two_projects
    p1 = ps[0]
    result = rivalry_reduction(instance, profile, p1, method_of_equal_shares, trials=20, sat_class=Cost_Sat)
    assert isinstance(result, int)

def test_no_supporters_returns_none_mes(simple_two_projects):
    instance, profile, ps = simple_two_projects
    p6 = Project("p6", 5)
    instance.update([p6])
    result = rivalry_reduction(instance, profile, p6, method_of_equal_shares, sat_class=Cost_Sat)
    assert result is None

@pytest.mark.slow
def test_realistic_scenario_mes():
    from pabutools import election
    path = "./tests/pabulib/poland_warszawa_2017_kolo.pb"
    instance, profile = election.parse_pabulib(path)
    alloc = method_of_equal_shares(instance, profile, sat_class=Cost_Sat)
    p3 = alloc[0]
    result = rivalry_reduction(instance, profile, p3, method_of_equal_shares, trials=5, sat_class=Cost_Sat)
    assert result <= 0

    for p in instance:
        if p not in alloc:
            p3 = p
            break
    result = rivalry_reduction(instance, profile, p3, method_of_equal_shares, trials=5, sat_class=Cost_Sat)
    assert result > 0

    profile.extend([ApprovalBallot([p3])] * (result + 20)) # may potentially fail its probabilistic
    assert p3 in method_of_equal_shares(instance, profile, sat_class=Cost_Sat)
