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
        self.A_NODE = MyNode('verb', 'a', False)
        self.CORRESPONDS_NODE = MyNode('konzept', 'korrespondiert_mit', False)
        # self.HERKUNFT_NODE = MyNode('konzept', 'hat_Herkunft', False)
        self.PARAM_NODE = MyNode('konzept', 'Parameter', True)
        self.MATERIAL_NODE = MyNode('konzept', 'Material', True)
        self.HAT_NAME_NODE = MyNode('konzept', 'hat_Name', False)
        self.HAT_PARAMETER_NODE = MyNode('konzept', 'hat_Parameter', False)

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
            if self.forward[subj].get(self.A_NODE) is not None:
                if self.forward[subj].get(self.HAT_PARAMETER_NODE) is not None:
                    for obj in self.forward[subj][self.A_NODE]:
                        if obj.new: # and obj.__eq__(self.MATERIAL_NODE)
                            new_mat.add(subj)
                        # self.forward[subj][pred].remove(obj)
        return new_mat


    def get_new_materials(self):
        new_material = self.search_for_new_material()
        new_mat_set = set()
        for mat in new_material:
            if self.forward.get(mat) is not None:
                if self.forward[mat].get(self.HAT_NAME_NODE) is not None:
                    new_mat_set = new_mat_set.union(self.forward[mat][self.HAT_NAME_NODE])
        # return new_mat_set
        return_set = set()
        for new_mat in new_mat_set:
            return_set.add(new_mat.name)
        return return_set

    def search_for_new_param(self, translation):
        new_param = set()
        for subj in self.forward:
            if self.forward[subj].get(self.A_NODE) is not None:
                for obj in self.forward[subj][self.A_NODE]:
                    if obj.name in translation and subj.new:
                        new_param.add(subj)
        return new_param

    def search_for_correspondings(self):
        new_cores = set()
        for subj in self.forward:
            if self.forward[subj].get(self.CORRESPONDS_NODE) is not None:
                for obj in self.forward[subj][self.CORRESPONDS_NODE]:
                    if subj.new:
                        new_cores.add(subj)
        return new_cores

    # def delete_new_param_part(self, params):
    #     for par in params:
    #         if self.forward.get(par) is not None:
    #             if self.forward[par].get(self.A_NODE) is not None:
    #                 if self.PARAM_NODE in self.forward[par][self.A_NODE]:
    #                     self.forward[par][self.HERKUNFT_NODE].remove(self.PARAM_NODE)

    def get_new_params(self, translation):
        new_val_param = self.search_for_new_param(translation)
        # self.delete_new_param_part(new_val_param)
        return new_val_param