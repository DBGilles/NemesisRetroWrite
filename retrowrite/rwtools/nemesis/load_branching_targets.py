import json


class BranchTargets:
    def __init__(self):
        self.targets = {}

    def append(self, target):
        target_func = target["function"]
        target_label = target["label"]
        if target_func not in self.targets.keys():
            self.targets[target_func] = []
        self.targets[target_func].append(target_label)

    def __repr__(self):
        return str(self.targets)

    def __getitem__(self, item):
        return self.targets[item]

def target_branches_from_json(json_file):
    with open(json_file) as f:
        data = json.load(f)
    targets = BranchTargets()
    for elem in data:
        targets.append(elem)
    return targets


if __name__ == '__main__':
    j_file = "/home/gilles/git-repos/NemesisRetroWrite/retrowrite/branching_targets.json"
    targets = target_branches_from_json(j_file)
    # print(targets)
    print(targets.targets)