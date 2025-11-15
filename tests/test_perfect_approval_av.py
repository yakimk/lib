import pytest

from pabutools.election import Project, Instance, ApprovalBallot, ApprovalProfile, total_cost
from pabutools import election
from pb_robustness_measures.remove_approval.perfect_approval_av import perfect_approval_av
from pb_robustness_measures.rules.greedyAV import greedy_av

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

def test_perfect_for_p1(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    result = perfect_approval_av(instance, profile, p1)
    assert isinstance(result, int)
    assert result == 1

def test_perfect_for_p2(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    result = perfect_approval_av(instance, profile, p2)
    assert isinstance(result, int)
    assert result == 2

def test_perfect_for_p3(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    result = perfect_approval_av(instance, profile, p3)
    assert isinstance(result, int)
    assert result == 2

def test_with_initial_allocation(setup_election):
    instance, profile, p1, p2, p3 = setup_election
    initial = [p1, p2]
    result = perfect_approval_av(instance, profile, p3, initial_budget_allocation=initial)
    assert result is None

@pytest.mark.slow
def test_real_world_target():
    path = "./tests/pabulib/poland_warszawa_2017_kolo.pb"
    instance, profile = election.parse_pabulib(path)
    projects = [p for p in instance]
    projects.sort()

    target = projects[len(projects)//2 +1 ]
    result = perfect_approval_av(instance, profile, target)
    res = greedy_av(instance, profile)
    assert target not in res

    print(target, res)
    diff = result

    for prof in profile:
        if target in prof:
            diff -= 1

    assert (isinstance(result, int) and result >= 0) or result is None
    profile.extend((diff-1) * [ApprovalBallot([target])])
    assert target not in greedy_av(instance, profile)
    profile.extend([ApprovalBallot([target])])
    assert target in greedy_av(instance, profile)



    target = projects[len(projects)//2 - 7]
    result = perfect_approval_av(instance, profile, target)
    res = greedy_av(instance, profile)

    assert target in res

    print(target, res)
    diff = result

    for prof in profile:
        if target in prof:
            diff -= 1
    
    print("diff", diff)

    assert (isinstance(result, int) and result >= 0) or result is None

    vote = 0 

    print("SCORE", profile.approval_score(target), result)
    for prof in profile:
        if diff < 0 and target in prof:
            prof.remove(target)
            diff += 1
        if target in prof:
            vote += 1

    print("SCORE", profile.approval_score(target), result)
    print("diff", diff)
    assert target in greedy_av(instance, profile)

    vote = 0
    for prof in profile:

        if target in prof: vote+=1
    
    print(vote)
    for prof in profile:
        if target in prof:
            prof.remove(target)
            break
    print("SCORE", profile.approval_score(target), result)
    assert target not in greedy_av(instance, profile)