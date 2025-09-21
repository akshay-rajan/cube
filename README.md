# cube

A version controller in `python` built to understand deeply `git` and version-control systems.

### About Git

In Git, every file or directory snapshot is stored by its `SHA-1` hash of the contents.
- **Objects**: Git wraps file data as `blob<size>\0<content>` and hashes it.
The resulting SHA-1 is used as the filename in `.git/objects`.
- **Tree**: A tree object is a snapshot of the directory, listing entries like `100644 blob a1b2c3 file.txt` for each file, effectively a “group photo” of the directory.
- **Commit**: A commit object records a snapshot: the root tree's hash, an optional parent commit, author/timestamp and a message.
- `HEAD`: A pointer to the current branch (`refs/heads/main`), which in turn points to the latest commit hash in that branch.

Git is a linked list of commit objects whose content is defined by hashes.
