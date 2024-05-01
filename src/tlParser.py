from tl import *

class MC_Phi(Phi):
    @translator
    def MC_ctl (self) :
        return self("MC_ctl", self)
    def _MC_ctl (self, node) :
        return self.__class__(node.kind,
                              *(self("MC_ctl", child) for child in node.children),
                              **node)
    def _MC_ctl_name (self, node) :
        return self.__class__(node.kind, **node)
    def _MC_ctl_bool (self, node) :
        return self.__class__(node.kind, **node)
    def _MC_ctl_not (self, node) :
        return self._MC_ctl(node)
    def _MC_ctl_and (self, node) :
        return self._MC_ctl(node)
    def _MC_ctl_or (self, node) :
        return self._MC_ctl(node)
    def _MC_ctl_imply (self, node) :
        return self._MC_ctl(node)
    def _MC_ctl_iff (self, node) :
        return self._MC_ctl(node)
    def __MC_ctl_quantifier(self, node):
        assert node.children[0].kind in "XFGU", f"{node.kind} must be followed by X, F, G or U"
        assert not node.actions, "actions not allowed on quantifiers"
        assert (not node.ufair) and (not node.wfair) and (not node.sfair), "fairness not allowed"
        for child in node.children[0].children :
            assert child.kind not in "FGURXWM", f"cannot nest {child.kind} in {node.kind}{node.children[0].kind}"

        actions = dict()
        for key, value in node.children[0].items():
            if key == "actions":
                if value.kind == "actions":
                    actions[key] = value.children[0]
                else:
                    actions[key] = value

        return self.__class__(node.kind + node.children[0].kind,
                              *(self("MC_ctl", child)
                                for child in node.children[0].children),
                              **node,
                              **actions)


    def _MC_ctl_A (self, node) :
        return self.__MC_ctl_quantifier(node)
    def _MC_ctl_E (self, node) :
        return self.__MC_ctl_quantifier(node)
    
def mc_parse(form):
    return parse(form,phiclass=MC_Phi).MC_ctl()





