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
        typ = tokens[0][0]
        if typ == "A":
            typ = "Added"
        elif typ == "M":
            typ = "Modified"
        elif typ == "D":
            typ = "Deleted"
        elif typ == "R":
            typ = "Renamed"
        elif typ == "C":
            typ = "Copied"
        elif typ == "?":
            typ = "Untracked"

        out.append((typ, tokens[1]))

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

def addRange(files, rng):
    for i in rng:
        err = exec("git add {}".format(files[i][1]))
        if err == "":
            print("Added {}".format(files[i][1]))
        else:
            print("Error: {}".format(err))

def main():
    parser = setupArgParse()
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    checkIfGit()

    if args.a:
        addFiles()
    elif args.c:
        commitFiles()
    else:
        addFiles()


def addFiles():
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
            addRange(files, rng)
            quitF = True

def commitFiles():
    files = getFiles()

    tracked = False
    for v in files:
        if v[0] == "Added":
            tracked = True
            break

    if len(files) == 0 or not tracked:
        print("Nothing to commit.")
        sys.exit(0)
    
    print("Files to commit:")

    for v in files:
        if v[0] == "Added":
            print("   " + v[1])

    msg = input("msg> ")

    if msg.strip() != "":
        out = exec("git commit -m {}".format(msg))
        tokens = out.split()
        branch = tokens[0][1:]
        hashB = tokens[1][:-1]
        print("Created commit {} on branch {}.".format(hashB, branch))

def setupArgParse():
    p = argparse.ArgumentParser(description="Fast Git management.")
    p.add_argument('-a', action="store_true", help="Add files to stage")
    p.add_argument('-c', action="store_true", help="Create new commit")
    return p

main()
