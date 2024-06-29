# Set up isolated, clean eopkg_venv python3.11 venv
#
# This is designed to be sourced from other bash scripts

set -euo pipefail

source shared_functions.bash

function prepare_venv () {
    if [[ -z "${PY3}" ]]; then
        die "Couldn't find supported python3 (3.11 || 3.12 || 3.10) interpreter, exiting!"
    else
        printInfo "Using python3 interpreter: ${PY3}"
    fi
    # Assume the user starts in the eopkg dir
    printInfo "Updating the eopkg git repo ..."
    # ensure we show the current branch
    git fetch && git checkout main && git pull && git branch

    printInfo "Set up a clean eopkg_venv venv ..."
    ${PY3} -m venv --system-site-packages --clear eopkg_venv
    source eopkg_venv/bin/activate
    ${PY3} -m pip install -r requirements.txt
    compile_iksemel_cleanly

    printInfo "Symlink eopkg-cli into the eopkg_venv bin/ directory so it can be executed as eopkg.py3 ..."
    ln -srvf ./eopkg-cli eopkg_venv/bin/eopkg.py3

    # get rid of any existing lines w/git ref version info
    sed "/__version__ += /d" -i pisi/__init__.py
    printInfo "pisi version variable BEFORE patching:":
    grep -Hn version pisi/__init__.py
    # append the git ref to __version__ on a new line
    gawk -i inplace 'BEGIN { "git rev-parse --short HEAD" | getline gitref } { print }; /__version__ = / { printf "%s %s\n", $1, "+= \" (" gitref ")\"" }' pisi/__init__.py
    printInfo "pisi version variable AFTER patching w/git revision:"
    grep -Hn version pisi/__init__.py
}

function compile_iksemel_cleanly () {
    # Solus is currently carrying a patch to iksemel that has not yet been upstreamed
    # clone iksemel fresh to ensure patches apply cleanly every time
    if [[ -d ../iksemel/build ]]; then
        printInfo "Uninstalling existing custom-compiled iksemel copy ..."
        pushd ../iksemel/
        sudo ninja uninstall -C build/
        popd
    fi
    printInfo "Set up a clean iksemel copy w/Solus patches ..."
    rm -rf ../iksemel/
    git clone https://github.com/Zaryob/iksemel.git ../iksemel/
    # fetch solus patches into iksemel dir
    pushd ../iksemel/
    # Need this specific commit to ensure patches apply cleanly; master corrupts memory?
    git checkout c929245c0953df514956252c288ae220f3411d8c
        for p in 0001-src-iks.c-Retain-py2-piksemel-behaviour.patch 0001-Escape-non-ASCII-characters.patch 0002-Escape-non-printable-ASCII-characters.patch
        do
            wget https://raw.githubusercontent.com/getsolus/packages/main/packages/i/iksemel/files/"${p}"
            patch -p1 -i "${p}"
        done
        # this should now build against the python in the eopkg_venv
        meson build -Dwith_python=true
        meson compile -C build/
        # Install iksemel, except for on Solus systems that already have iksemel installed
        grep -q 'NAME="Solus"' /etc/os-release && find /usr/lib* -name libiksemel.so -quit || \
        sudo meson install -C build/
    popd
    # symlink the iksemel python C module into our eopkg_venv
    local py3=$(basename "${PY3}")
    printInfo "Symlink the newly built Solus-patched iksemel python C-extension into the eopkg_venv ..."
    ln -srvf "$(find ../iksemel/build/python -name 'iksemel.cpython*.so' -print -quit)" eopkg_venv/lib/"${py3}"/site-packages/
    ls -l eopkg_venv/lib/"${py3}"/site-packages/*.so
}

function help () {
    cat << EOF

    1. To activate the newly prepared eopkg venv, execute one of:

       source eopkg_venv/bin/activate
       source eopkg_venv/bin/activate.fish
       source eopkg_venv/bin/activate.zsh

       ... depending on which shell you use.

    2. To run a command with elevated privileges via sudo inside the venv, execute:

       sudo -E env PATH="\${PATH}" <the command>

    3. When you are done, execute:

       deactivate

       ... to exit the eopkg venv.

EOF
}
