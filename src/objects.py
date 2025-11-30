import os
import pickle
from src.constants import NAME
from src import utils


class Index:
    """Index object to track files staged for commit."""

    path = f".{NAME}/index"

    def __init__(self, from_file=True):
        if from_file and os.path.isfile(self.path):
            with open(self.path, 'rb') as f:
                data = f.read()
                loaded_index = pickle.loads(data)
                self.entries = loaded_index.entries
        else:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.entries = {}
            self._store()

    def _store(self):
        data =  pickle.dumps(self)
        with open(self.path, 'wb') as f:
            f.write(data)

    def add(self, path: str, hash: str) -> None:
        self.entries[path] = hash
        self._store()

    def _contains(self, path: str) -> bool:
        return path in self.entries

    def remove(self, path: str) -> None:
        if self._contains(path):
            hash = self.entries[path]
            del self.entries[path]
            utils.delete_object(hash)
            self._store()

    def overwrite(self, path: str, hash: str) -> None:
        if self._contains(path):
            old_hash = self.entries[path]
            utils.delete_object(old_hash)
        self.entries[path] = hash
        self._store()

    def clear(self) -> None:
        self.entries.clear()
        self._store()

    def list_entries(self):
        return self.entries.items()


class Tree:
    """
    A tree with subtrees represents a directory, meanwhile one without a subtree is a file.
    """
    def __init__(self, name:str, hash=None) -> None:
        self.name = name
        self.hash = hash
        self.subtrees: list[Tree] = []

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

    def _is_file(self) -> bool:
        return len(self.subtrees) == 0 and self.hash is not None

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

    def merge(self, other: 'Tree') -> None:
        """Merge another tree into the current tree"""
        if self._is_file():
            if other._is_file():
                self.hash = other.hash
            return

        new_trees = []
        for subtree_1 in self.subtrees:
            for subtree_2 in other.subtrees:
                if subtree_1 == subtree_2:
                    subtree_1.merge(subtree_2)
                    new_trees.append(subtree_2)
                    break

        for subtree_2 in other.subtrees:
            if subtree_2 not in new_trees:
                self.subtrees.append(subtree_2)        
        

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
