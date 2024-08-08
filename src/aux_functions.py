def is_hierarchical(states):
    hierarchical = False
    for elem in states:
        if "children" in elem:
            hierarchical = True
            break
    
    return hierarchical


