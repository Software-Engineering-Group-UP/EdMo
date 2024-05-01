from tlParser import *
from KripkeTransitionSystem import *


def check_formula(phi, kts):
    # categorize phi to be checked
    S = set()

    if phi.kind == "bool":
        S = check_bool(phi, kts)

    if phi.kind == "name":
        S = check_atom(phi, kts)

    if phi.kind == "not":
        S = check_not(phi, kts)

    if phi.kind == "and":
        S = check_and(phi, kts)

    if phi.kind == "or":
        S = check_or(phi, kts)

    if phi.kind == "imply":
        S = check_imply(phi, kts)

    if phi.kind == "iff":
        S = check_iff(phi, kts)

    if phi.kind == "EX":
        S = check_EX(phi, kts)

    if phi.kind == "AX":
        S = check_AX(phi, kts)

    if phi.kind == "EF":
        S = check_EF(phi, kts)

    if phi.kind == "AF":
        S = check_AF(phi, kts)

    if phi.kind == "EG":
        S = check_EG(phi, kts)

    if phi.kind == "AG":
        S = check_AG(phi, kts)

    if phi.kind == "EU":
        S = check_EU(phi, kts)

    if phi.kind == "AU":
        S = check_AU(phi, kts)

    return S


def subgraph(phi, kts):
    # phi.actions != None
    # currently only supports actions as a single atom or multiple atoms combined with the "|" operator
    acts = []
    if phi.actions.kind == "name":
        acts = [phi.actions.value]
    if phi.actions.kind == "or":
        for c in phi.actions.children:
            acts.append(c.value)

    newTransitions = []
    for t in kts.transitions:
        if t["trigger"] in acts:
            newTransitions.append(t)
    return KripkeTransitionSystem(states=kts.states, transitions=newTransitions, initial=kts.initial)


def check_bool(phi, kts):
    # phi.kind = bool
    # all states inherently have True as an AP
    S = set()
    if phi.value == True:
        S = kts.getStateSet()
    return S


def check_atom(phi, kts):
    # phi.kind = name
    S = set()
    for s in kts.states:
        if phi.value in s["tags"]:
            S.add(s["name"])
    return S


def check_not(phi, kts):
    # phi.kind = not
    childSet = check_formula(phi.children[0], kts)
    S = kts.getStateSet().difference(childSet)
    return S


def check_and(phi, kts):  # todo: and/or with more than 2 children
    # phi.kind = and
    leftChildSet = check_formula(phi.children[0], kts)
    rightChildSet = check_formula(phi.children[1], kts)
    S = leftChildSet.intersection(rightChildSet)
    return S


def check_or(phi, kts):
    # phi.kind = or
    leftChildSet = check_formula(phi.children[0], kts)
    rightChildSet = check_formula(phi.children[1], kts)
    S = leftChildSet.union(rightChildSet)
    return S


def check_imply(phi, kts):
    # phi.kind = imply
    premise = check_formula(phi.children[0], kts)
    conclusion = check_formula(phi.children[1], kts)
    S = kts.getStateSet().difference(premise)
    S = S.union(conclusion)
    return S


def check_iff(phi, kts):
    # phi.kind = iff
    leftChildSet = check_formula(phi.children[0], kts)
    rightChildSet = check_formula(phi.children[1], kts)
    S = kts.getStateSet().difference(leftChildSet)
    S = S.difference(rightChildSet)
    S = S.union(leftChildSet.intersection(rightChildSet))
    return S


def check_EX(phi, kts):
    # phi.kind = EX
    if phi.actions != None:
        kts = subgraph(phi, kts)
    S = set()
    childSet = check_formula(phi.children[0], kts)
    for s in kts.states:
        if kts.successors(s["name"]).intersection(childSet) != set():
            S.add(s["name"])
    return S


def check_AX(phi, kts):
    # phi.kind = AX
    S = set()
    if phi.actions != None:
        kts = subgraph(phi, kts)
    childSet = check_formula(phi.children[0], kts)
    for s in kts.states:
        if kts.successors(s["name"]).issubset(childSet) & (kts.successors(s["name"]) != set()):
            S.add(s["name"])
    return S


def check_EF(phi, kts):
    # phi.kind = EF
    if phi.actions != None:
        kts = subgraph(phi, kts)

    review_set = check_formula(phi.children[0], kts)
    final_set = review_set.copy()
    visited = set()

    while review_set != set():
        current_state = next(iter(review_set))
        pre = kts.predecessors(current_state)
        review_set = review_set.union(pre)
        final_set = final_set.union(pre)

        visited.add(current_state)
        review_set = review_set.difference(visited)  # make sure previously visited states are removed

    return final_set


def check_AF(phi, kts):
    # phi.kind = AF
    if phi.actions != None:
        kts = subgraph(phi, kts)

    suc_count = kts.suc_count()
    review_set = check_formula(phi.children[0], kts)
    final_set = review_set.copy()
    visited = set()

    while review_set != set():
        current_state = next(iter(review_set))
        pre = kts.predecessors(current_state)
        for s in pre:
            suc_count[s] -= 1
            if suc_count[s] == 0:
                review_set.add(s)
                final_set.add(s)

        visited.add(current_state)
        review_set = review_set.difference(visited)

    return final_set


def check_EG(phi, kts):
    # phi.kind = EG
    if phi.actions != None:
        kts = subgraph(phi, kts)

    final_set = check_formula(phi.children[0], kts)
    review_set = kts.getStateSet().difference(final_set)
    suc_count = kts.suc_count()
    visited = set()

    while review_set != set():
        current_state = next(iter(review_set))
        pre = kts.predecessors(current_state)
        for s in pre:
            if s in final_set:
                suc_count[s] -= 1
                if suc_count[s] == 0:
                    final_set.remove(s)
                    review_set.add(s)

        visited.add(current_state)
        review_set = review_set.difference(visited)

    return final_set


def check_AG(phi, kts):
    # phi.kind = EG
    if phi.actions != None:
        kts = subgraph(phi, kts)

    final_set = check_formula(phi.children[0], kts)
    review_set = kts.getStateSet().difference(final_set)
    visited = set()

    while review_set != set():
        current_state = next(iter(review_set))
        pre = kts.predecessors(current_state)
        for s in pre:
            if s in final_set:
                final_set.remove(s)
                review_set.add(s)

        visited.add(current_state)
        review_set = review_set.difference(visited)

    return final_set


def check_EU(phi, kts):
    # phi.kind = EU
    if phi.actions != None:
        kts = subgraph(phi, kts)

    leftChildSet = check_formula(phi.children[0], kts)
    rightChildSet = check_formula(phi.children[1], kts)
    review_set = rightChildSet.copy()
    final_set = rightChildSet.copy()
    visited = set()

    while review_set != set():
        current_state = next(iter(review_set))
        pre = kts.predecessors(current_state)
        for s in pre:
            if s in leftChildSet:
                review_set.add(s)
                final_set.add(s)

        visited.add(current_state)
        review_set = review_set.difference(visited)

    return final_set


def check_AU(phi, kts):
    # phi.kind = AU
    if phi.actions != None:
        kts = subgraph(phi, kts)

    suc_count = kts.suc_count()
    leftChildSet = check_formula(phi.children[0], kts)
    rightChildSet = check_formula(phi.children[1], kts)
    review_set = rightChildSet.copy()
    final_set = rightChildSet.copy()
    visited = set()

    while review_set != set():
        current_state = next(iter(review_set))
        pre = kts.predecessors(current_state)
        for s in pre:
            suc_count[s] -= 1
            if (s in leftChildSet) & (suc_count[s] == 0):
                review_set.add(s)
                final_set.add(s)

        visited.add(current_state)
        review_set = review_set.difference(visited)

    return final_set
