import os
import sys
import signal
import argparse
import subprocess

# Handle the Ctrl+C exiting
def signal_handler(sig, frame):
    sys.exit(0)

# Checks if currently in Git repo
def checkIfGit():
    if not os.path.exists("./.git"):
        print("Not currently in a git repo.")
        sys.exit()

# Main function for executing shell commands and returning the output
def exec(cmd):
    r = subprocess.check_output(cmd, shell=True)
    return r.decode("utf-8")

def getFiles():
    output = exec("git status --porcelain").split("\n")

    out = []

    for v in output[:-1]:
        tokens = v.split()
        typ = v[0:2]
        if typ[0] == "A" or typ[1] == " ":
            typ = "Added"
        elif typ[1] == "M":
            typ = "Modified"
        elif typ[1] == "D":
            typ = "Deleted"
        elif typ[1] == "R":
            typ = "Renamed"
        elif typ[1] == "C":
            typ = "Copied"
        elif typ[0] == "?":
            typ = "Untracked"

        out.append((typ, tokens[1], v[0:2]))

    return out

def parseRange(cmd, maxN):
    selection = set()
    invalid = set()
    tokens = [x.strip() for x in cmd.split(",")]

    noAdd = False
    for v in tokens:
        if len(v) > 0:
            if v == ".":
                v = "0-%s"%(maxN-1)
            if v[:1] == "<":
                v = "0-%s"%(v[1:])
            if v[:1] == "!":
                if int(v[1:]) in selection:
                    selection.remove(int(v[1:]))
                noAdd = True

        try:
            if not noAdd:
                num = int(v)
                if abs(num) <= maxN-1:
                    selection.add(num)
                else:
                    invalid.add(v)
            else:
                noAdd = False
        except:
            try:
                token = [int(k.strip()) for k in v.split('-')]
                if len(token) > 1:
                    token.sort()
                    first = token[0]
                    last = token[len(token)-1]
                    for x in range(first, last+1):
                        selection.add(x)
            except:
                invalid.add(v)

    if len(invalid) > 0:
        print("Invalid set: " + str(', '.join(invalid)))
        return None

    return selection

def addRange(files, rng, execute=True):
    for i in rng:
        err = ""
        if execute:
            err = exec("git add {}".format(files[i][1]))
        if err == "":
            files[i] = ("Added", files[i][1])
            print("Added {}.".format(files[i][1]))
        else:
            print("Error: {}".format(err))

def pushCommit(msg):
    out = exec('git commit -m \"{}\"'.format(msg))
    tokens = out.split()
    branch = tokens[0][1:]
    hashB = tokens[1][:-1]
    print("Created commit {} on branch {}.".format(hashB, branch))

def main():
    parser = setupArgParse()
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    checkIfGit()

    if args.a:
        addFiles()
    elif args.c:
        commitFiles()
    elif args.s:
        snapshot()
    else:
        addFiles()


def addFiles(execute=True):
    files = getFiles()
    
    if len(files) == 0:
        print("Nothing to add.")
        sys.exit(0)

    print("Select files to add:")

    for i, v in enumerate(files):
        print("{0:3d}. {1:10s} {2}".format(i, v[0], v[1]))

    quitF = False

    while not quitF:
        cmd = str(input("> "))

        if cmd == "q" or cmd == "":
            sys.exit(0)

        rng = parseRange(cmd, len(files))

        if rng != None:
            addRange(files, rng, execute)
            if not execute:
                return (files, rng)
            quitF = True

def commitFiles(execute=True, stats=None):
    files = None

    if stats:
        files = stats
    else:
        files = getFiles()

    tracked = False
    for v in files:
        if v[0] == "Added":
            tracked = True
            break

    if execute:
        if len(files) == 0 or not tracked:
            print("Nothing to commit.")
            sys.exit(0)
    
    print("Files to commit:")

    for v in files:
        if v[0] == "Added":
            print("   " + v[1])

    msg = input("msg> ")

    if msg.strip() != "":
        if execute:
            pushCommit(msg)
        else:
            return (msg)

def snapshot():
    addArgs = addFiles(False)
    comArgs = commitFiles(False, addArgs[0])
    if comArgs.strip() != "":
        addRange(addArgs[0], addArgs[1], True)
        pushCommit(comArgs)

def setupArgParse():
    p = argparse.ArgumentParser(description="Fast Git management.")
    p.add_argument('-a', action="store_true", help="Add files to stage")
    p.add_argument('-c', action="store_true", help="Create new commit")
    p.add_argument('-s', action="store_true", help="New snapshot, choose files to add and commit")
    return p

main()
