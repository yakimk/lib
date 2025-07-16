from collections.abc import Collection
from pabutools.rules.budgetallocation import BudgetAllocation
from pabutools.election import Instance, Project, total_cost, AbstractApprovalProfile
from pabutools.tiebreaking import TieBreakingRule, lexico_tie_breaking
import matplotlib.pyplot as plt

def av_graph(
    instance: Instance,
    profile: AbstractApprovalProfile,
    tie_breaking: TieBreakingRule | None = None,
    ):
    """
    Given an instance produces a graph of (supperters, cost) for each project
    and draws a curve of (move, budget left).
    As a conseqeunce of this definition every project lying below the curve will be selected by 
    Seq - AV. 

    Also several measures on AV can be interpreted by looking at this graph.
    For instance `optimal cost` is simply a vertical projection of a point onto a curve
    `optimal approval` is horizontal projection.


    After choosing appropriate coordinates (i.e. deciding on how much one new voter costs for example)
    We might also consider measure that is the distance to the curve. 
    But note that for every project this measure would be dependent on the choice of coordinates.
    But after choice of coordinates for each candidate the measure of distance to the graph is well-defined. 
    We might call it "subjective stability" or "perceived stability" (as it depends on the choice of coordinates by candidate).
    The point on the curve that is the projection for a given candidate is called optimal (it need not be unique of course).

    We can also define a measure of `rivalry` in terms of "how many optimal points 
    of other candidates are close to my optimal point". A kind of naive approach would be 
    to define it as a length of an arc of the curve (centered at an optimal point for a chosen candidate) 
    that contains for example 10% of optimal points for other candidates or something like that. 

    Also this allows us to define what we call `fundamental region` of an election,
    which is simply (don't know what it represents yet, but seems interesting)
    """
    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking


    allocation = BudgetAllocation()
    # current_cost = total_cost(allocation)
    remaining = [p for p in instance if p not in allocation]
    scores = {p: profile.approval_score(p) for p in remaining}
    ordered: list[Project] = []
    to_order = set(remaining)
    while to_order:
        max_score = max(scores[p] for p in to_order)
        tied = [p for p in to_order if scores[p] == max_score]
        ordered_ties = tie_breaking.order(instance, profile, tied)
        ordered.extend(ordered_ties)
        to_order.difference_update(tied)

    supporters = [profile.approval_score(p) for p in ordered]
    costs = [p.cost for p in ordered]
    names = [p.name for p in ordered]

    budget_levels = []
    selected = []
    remaining_budget = instance.budget_limit
    for p in ordered:
        budget_levels.append(remaining_budget)
        if profile.approval_score(p) > 0 and remaining_budget >= p.cost:
            selected.append(True)
            remaining_budget -= p.cost
        else:
            selected.append(False)

    fig, ax = plt.subplots(figsize=(10,6))
    colors = ['red' if sel else 'blue' for sel in selected]
    ax.scatter(supporters, costs, c=colors)
    for x, y, label in zip(supporters, costs, names):
        ax.annotate(label, (x, y), textcoords="offset points", xytext=(5,5))


    for i, y in enumerate(budget_levels):
        if i + 1 < len(supporters):
            x0, x1 = supporters[i], supporters[i+1]
            start, end = max(x0, x1), min(x0, x1)
            ax.hlines(y, start, end)


    for i in range(len(supporters) - 1):
        x = supporters[i+1]
        y0 = budget_levels[i]
        y1 = budget_levels[i+1]
        bottom, top = min(y0, y1), max(y0, y1)
        ax.vlines(x, bottom, top)

    ax.set_xlabel('Number of Supporters')
    ax.set_ylabel('Project Cost')
    ax.set_title('Projects by Supporters vs Cost with Remaining Budget Segments')
    ax.invert_xaxis()
    plt.show()
