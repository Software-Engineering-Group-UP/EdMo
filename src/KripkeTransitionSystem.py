
class KripkeTransitionSystem:

    def __init__(self, states, transitions, initial):
        self.states = states
        self.transitions = transitions
        self.initial = initial

    def successors(self, state):
        successors = []
        for t in self.transitions:
            if t["source"] == state:
                successors.append(t["dest"])
        return set(successors)

    def predecessors(self, state):
        predecessors = []
        for t in self.transitions:
            if t["dest"] == state:
                predecessors.append(t["source"])
        return set(predecessors)
    
    def suc_count(self):
        suc_count = {}
        for s in self.states:
            suc_count[s["name"]] = len(self.successors(s["name"]))

        return suc_count

    
    def getTags(self, state):
        tags = []
        for s in self.states:
            if s["name"] == state:
                tags.append(s["tags"])
        return tags
    
    def getStateSet(self):
        stateSet = set()
        for s in self.states:
            stateSet.add(s["name"])

        return stateSet