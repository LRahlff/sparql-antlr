from MyNode import MyNode


def privat_add(diction, subj, pred, obj):
    if diction.get(subj) is None:
        diction[subj] = {}
    if diction[subj].get(pred) is None:
        diction[subj][pred] = set()
    diction[subj][pred].add(obj)

class MyRelationTree:
    def __init__(self):
        self.forward = {}
        self.reverse = {}

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

        return

    def search_for_new_material(self):
        new_mat = set()
        for subj in self.forward:
            for pred in self.forward[subj]:
                if pred.name == 'a':
                    for obj in self.forward[subj][pred]:
                        if obj.name == 'Material_Neu':
                            new_mat.add(subj)
                            # self.forward[subj][pred].remove(obj)
        return new_mat


    def get_new_materials(self):
        new_material = self.search_for_new_material()
        new_mat_set = set()
        for mat in new_material:
            if self.forward.get(mat) is not None:
                node = MyNode('konzept', 'hat_Name')
                if self.forward[mat].get(node) is not None:
                    new_mat_set = new_mat_set.union(self.forward[mat][node])
        # return new_mat_set
        return_set = set()
        for new_mat in new_mat_set:
            return_set.add(new_mat.name)
        return return_set

    def search_for_new_param(self):
        new_param = set()
        for subj in self.forward:
            for pred in self.forward[subj]:
                if pred.name == 'a':
                    for obj in self.forward[subj][pred]:
                        if obj.name == 'Parameter_Neu':
                            new_param.add(subj)
                            # self.forward[subj][pred].remove(obj)
        return new_param
    def delete_new_param_part(self, params):
        for par in params:
            if self.forward.get(par) is not None:
                node = MyNode('verb', 'a')
                if self.forward[par].get(node) is not None:
                    node2 = MyNode('konzept', 'Parameter_Neu')
                    if node2 in self.forward[par][node]:
                        self.forward[par][node].remove(node2)

    def get_new_params(self):
        new_val_param = self.search_for_new_param()
        self.delete_new_param_part(new_val_param)
        return new_val_param