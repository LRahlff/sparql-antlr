from MyNode import MyNode, Relation


def privat_add(diction, subj, pred, obj):
    if diction.get(subj) is None:
        diction[subj] = {}
    if diction[subj].get(pred) is None:
        diction[subj][pred] = set()
    diction[subj][pred].add(obj)
    for (key) in diction:
        if subj.__eq__(key):
            key.new = subj.new or key.new

class MyRelationTree:
    def __init__(self):
        self.forward = {}
        self.reverse = {}
        self.A_NODE = MyNode('verb', 'a', False)
        self.CORRESPONDS_NODE = MyNode('konzept', 'korrespondiert_mit', False)
        # self.PARAM_NODE = MyNode('konzept', 'Parameter', True)
        # self.MATERIAL_NODE = MyNode('konzept', 'Material', True)
        self.HAT_NAME_NODE = MyNode('konzept', 'hat_Name', False)
        self.IST_NEUE_ANNAHME = MyNode('konzept', 'ist_neue_Annahme', True)
        self.HAT_PARAMETER_NODE = MyNode('konzept', 'hat_Parameter', False)
        self.HAT_ZUSTANDSGROESSE = MyNode('konzept', 'hat_Zustandsgroesse', False)
        self.HAT_ANNAHME = MyNode('konzept', 'hat_Annahme', False)
        self.HAT_NEUE_ABFRAGE_ANNAHME = MyNode('konzept', 'hat_neue_Abfrage_Annahme', True)
        self.TRUE_NODE = MyNode('booleanliteral', 'True', True)
        self.HAT_WERT_NODE = MyNode('konzept', 'hat_Wert', False)
        self.HAT_WERT_LESS_NODE = MyNode('konzept', 'hat_Wert', False, Relation.LESS)
        self.HAT_WERT_GREATER_NODE = MyNode('konzept', 'hat_Wert', False, Relation.GREATER)

    def add(self, subj, pred, obj):
        privat_add(self.forward, subj, pred, obj)
        privat_add(self.reverse, obj, pred, subj)

    def traverseVars(self):
        for var in self.forward:
            if var.is_var():
                for pred in self.forward[var]:
                    if pred.is_same():
                        if self.reverse.get(var) is not None:
                            for pred2 in self.reverse[var]:
                                for subj2 in self.reverse[var][pred2]:
                                    for obj1 in self.forward[var][pred]:
                                        self.add(subj2, pred2, obj1)
                                    if var in self.forward[subj2][pred2]:
                                        self.forward[subj2][pred2].remove(var)
                    if pred.is_less():
                        if self.reverse.get(var) is not None:
                            for pred2 in self.reverse[var]:
                                for subj2 in self.reverse[var][pred2]:
                                    for obj1 in self.forward[var][pred]:
                                        pred2_new = MyNode(pred2.type, pred2.name, pred2.new, pred.rel, pred.nr_of_interval)
                                        self.add(subj2, pred2_new, obj1)
                                    if var in self.forward[subj2][pred2]:
                                        self.forward[subj2][pred2].remove(var)
                    if pred.is_greater():
                        if self.reverse.get(var) is not None:
                            for pred2 in self.reverse[var]:
                                for subj2 in self.reverse[var][pred2]:
                                    for obj1 in self.forward[var][pred]:
                                        pred2_new = MyNode(pred2.type, pred2.name, pred2.new, pred.rel, pred.nr_of_interval)
                                        self.add(subj2, pred2_new, obj1)
                                    if var in self.forward[subj2][pred2]:
                                        self.forward[subj2][pred2].remove(var)
        return

    def search_for_new_objects(self):
        new_obj = set()
        for subj in self.forward:
            if self.forward[subj].get(self.HAT_NEUE_ABFRAGE_ANNAHME) is not None:
                for obj in self.forward[subj][self.HAT_NEUE_ABFRAGE_ANNAHME]:
                    new_obj.add(obj)
        return new_obj

    def get_named_pais_inner(self, pairs, subj, koncept, translation, subname, reverse):
        for obj in self.forward[subj][koncept]:
            objname = obj.name
            if self.forward.get(obj) is not None:
                if self.forward[obj].get(self.HAT_NAME_NODE) is not None:
                    for names in self.forward[obj][self.HAT_NAME_NODE]:
                        objname = names.name
            if translation is not None and translation.get(objname) is not None:
                objname = translation[objname]
            if reverse:
                pairs.add("('" + objname + "', '" + subname + "')")
            else:
                pairs.add("('" + subname + "', '" + objname + "')")

    def get_named_pairs(self, subj, koncept, translation = None, reverse = False, allow_subject_name = False):
        pairs = set()
        if self.forward.get(subj) is not None:
            if self.forward[subj].get(koncept) is not None:
                if allow_subject_name and self.forward[subj].get(self.HAT_NAME_NODE) is not None:
                    for names in self.forward[subj][self.HAT_NAME_NODE]:
                        self.get_named_pais_inner(pairs, subj, koncept, translation, names.name, reverse)
                else:
                    self.get_named_pais_inner(pairs, subj, koncept, translation, subj.name, reverse)

        return pairs

    def get_hierarchy(self):
        pairs = set()
        for subj in self.forward:
            pairs = pairs.union(self.get_named_pairs(subj, self.HAT_NEUE_ABFRAGE_ANNAHME, reverse=True, allow_subject_name=True))
        return pairs

    # def get_new_materials(self, new_obj):
    #     return list(map(lambda node: node.name, new_obj))

    def get_new_param_ids(self, new_obj, translation):
        pairs = {}
        for subj in new_obj:
            if self.reverse.get(subj) is not None and self.reverse[subj].get(self.HAT_PARAMETER_NODE) is not None:
                for obj in self.reverse[subj][self.HAT_PARAMETER_NODE]:
                    objname = obj.name
                    if self.forward.get(obj) is not None and self.forward[obj].get(self.HAT_NAME_NODE) is not None:
                        for names in self.forward[subj][self.HAT_NAME_NODE]:
                            objname = names.name
                    if pairs.get(objname) is None:
                        pairs[objname] = set()
                    pairs[objname] = pairs[objname].union(self.get_named_pairs(subj, self.A_NODE, translation))
        triples = set()
        for obj in pairs:
            for pair in pairs[obj]:
                triples.add("('" + obj + "', " + pair[1:])
        return triples

    def get_new_params(self, new_obj):
        new_param = set()
        for subj in new_obj:
            if self.forward.get(subj) is not None:
                if self.forward[subj].get(self.HAT_PARAMETER_NODE) is not None:
                    for sub_param in self.forward[subj][self.HAT_PARAMETER_NODE]:
                        new_param.add(sub_param)
        return new_param

    # def get_new_param_ids(self, new_values, translation):
    #     pairs = set()
    #     for subj in new_values:
    #         pairs = pairs.union(self.get_named_pairs(subj, self.A_NODE, translation))
    #     return pairs

    def get_values(self, new_values):
        pairs = set()
        for subj in new_values:
            found_less = False
            found_greater = False
            less_val = 0.0
            greater_val = 0.0
            if self.forward[subj].get(self.HAT_WERT_NODE) is not None:
                for obj in self.forward[subj][self.HAT_WERT_NODE]:
                    if obj.type == 'numeric' and obj.rel == Relation.EQUAL:
                        pairs.add("('" + subj.name + "', " + obj.name + ")")
            if self.forward[subj].get(self.HAT_WERT_LESS_NODE) is not None:
                for obj in self.forward[subj][self.HAT_WERT_LESS_NODE]:
                    if obj.type == 'numeric':
                        found_less = True
                        less_val = float(obj.name)
            if self.forward[subj].get(self.HAT_WERT_GREATER_NODE) is not None:
                for obj in self.forward[subj][self.HAT_WERT_GREATER_NODE]:
                    if obj.type == 'numeric':
                        found_greater = True
                        greater_val = float(obj.name)
            if found_less and found_greater:
                interval = (less_val - greater_val) / (subj.nr_of_interval - 1)
                for i in range(subj.nr_of_interval):
                    pairs.add("('" + subj.name + "', " + str(greater_val + i * interval) + ")")
        return pairs

    def print_tree(self):
        for s in self.forward:
            print(s.name)
            for p in self.forward[s]:
                print("  " + p.name)
                for o in self.forward[s][p]:
                    print("    " + o.name)
    def print_tree_rev(self):
        for s in self.reverse:
            print(s.name)
            for p in self.reverse[s]:
                print("  " + p.name)
                for o in self.reverse[s][p]:
                    print("    " + o.name)
    def print_tree_dict(self, tree):
        for s in tree:
            print(s.name)
            for p in tree[s]:
                print("  " + p.name + " " + str(p.rel))
                for o in tree[s][p]:
                    print("    " + o.name)
