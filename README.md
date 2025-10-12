# cube

A version controller in `python` built to understand deeply about `git` and version-control systems.

## features

1. Initialize the repository with `python3 main.py init`
2. Stage file / directory with `python3 main.py add [filename/directory]`.
3. Commit the staged changes with `python3 main.py commit -m "message"`.
4. Get the current status of the repo with `python3 main.py status`
5. Create a new branch using `python3 main.py branch [branchname]`. 
6. List all branches with `python3 main.py branch`.
7. Checkout to another branch using `python3 main.py switch [branchname]`. (*Only changes the reference*)
8. Use `.cubeignore` to skip files from version controlling.
9. Get commit logs by running `python3 main.py log`.
10. Remove version controlling from the repo using `python3 main.py undo`.

---

[Gist on Git and GitHub](https://gist.github.com/akshay-rajan/2c5cdd4e8996a6829b89398814cffdc1)
