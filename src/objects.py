import os
import pickle
from src import utils


class Tree:
    """
    Commit tree.
    A tree with subtrees represents a directory, meanwhile one without a child is a file.
    """
    def __init__(self, name:str, hash=None) -> None:
        self.name = name
        self.hash = hash
        self.subtrees: Tree = []

    def __eq__(self, other) -> bool:
        return isinstance(other, Tree) and self.name == other.name

    def __str__(self):
        return self._str_helper("")

    def _str_helper(self, prefix):
        res = f"{self.name}"
        for i, subtree in enumerate(self.subtrees):
            is_last = i == len(self.subtrees) - 1
            if is_last:
                res += f"\n{prefix}└── {subtree._str_helper(prefix + '    ')}"
            else:
                res += f"\n{prefix}├── {subtree._str_helper(prefix + '│   ')}"
        return res

    def add_subtrees(self, path, hash) -> None:
        normalized_path = os.path.normpath(path)
        if os.path.basename(path) == normalized_path:
            file = Tree(normalized_path, hash)
            self.subtrees.append(file)
            return
        
        parts = normalized_path.split(os.sep)
        first_dirname, child_path = parts[0], os.sep.join(parts[1:])
        dir = Tree(first_dirname)
        
        for subtree in self.subtrees:
            if subtree == dir:
                subtree.add_subtrees(child_path, hash)
                return

        dir.add_subtrees(child_path, hash)
        self.subtrees.append(dir)


class Commit:
    """Commit object."""
    def __init__(self, tree: Tree, parent: str = None, message: str = None):
        self.tree = tree
        self.parent = parent
        self.message = message

    def __str__(self):
        parent_str = self.parent if self.parent else "None"
        return (
            f"COMMIT (Parent: {parent_str}, Message: {self.message})\n"
            f"{self.tree}\n"
        )
    
    @staticmethod
    def from_bytes(data: bytes):
        return pickle.loads(data)
    
    @staticmethod
    def from_hash(hash: str):
        object_path = utils.get_object_path(hash)
        with open(object_path, 'rb') as f:
            data = f.read()
            return Commit.from_bytes(data)

    def get_parent(self):
        if not self.parent:
            return None
        return Commit.from_hash(self.parent)
