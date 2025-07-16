## Installing dependencies
```
poetry install
```

## Running tests

Run all tests 
```
pytest
```

Run only the quick tests (don't run tests on real world instances)
```
pytest -m "not slow" 
```

Run only tests on real world instances
```
pytest -m "slow" 
```

---


|                      | Greedy-AV              | Phragmen         | MES              |
|----------------------|------------------------|------------------|------------------|
| optimal-cost         |       [x]              |       [x]        | naive, not O(1)  |
| optimist-remove      |       [x]              |                  |                  |
| 50%-remove           |       [x]              |                  |                  |
| pessimist-remove     |       [x]              |                  |                  |
| add-complement       |       [x]              |    sampling?     |       [x]        |
| limited-bribery      |       [x]              |       [x]        |       [x]        |


`p` - a fixed project (candidate)

## Optimal cost
Returns the maximal cost of `p` should have in order to be selected.

## Optimist remove
Largest number of supporters of `p` that can stop voting for `p` with `p` being still elected.

## 50% Remove 
Largest number of supporters of `p` that can stop voting for `p` with `p` being still elected on average in 50% of cases.

## Pessimist Remove 
Smallest number of supporters of `p` that can stop voting for `p` with `p` being still elected.

## Add complement
How many voters approving of evert project except `p` could we add with `p` still being selected

## Limited Bribery
1. If `p` is selected we check how many supporters of on average have to vote for everyone except `p`, for `p` to be omitted in 50% of cases.
2. If `p` is not selected in the first place, we check how many non-supporters of `p` have to vote exclusively for `p` for it to be selected in 50% cases on average.

---

<!-- ## Greedy-AV
1. Optimal cost
    We can easily compute the optimal cost that a selected project should have.
2. Pessimist-remove = 50%-remove = Optimist-remove 
    So we call this measure for AV Perfect Approval i.e. the minimal amount of votes it should get to be selected (given a certain price).
3. Add complement is essentially the same as Perfect Approval. 

## Phragmen
1. Optimal cost
    We can compute the optimal cost a project should have to get selected, by keeping a maximal value of "money" its supporters have accumulated at moments whenever we select a new project.

2.  -->