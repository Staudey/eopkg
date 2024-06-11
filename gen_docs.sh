#!/usr/bin/env bash

# Credit to swupd developers: https://github.com/clearlinux/swupd-client

MANPAGES="man/eopkg.1"

for MANPAGE in ${MANPAGES}; do \
    ronn --roff < ${MANPAGE}.md > ${MANPAGE}; \
    ronn --html < ${MANPAGE}.md > ${MANPAGE}.html; \
done
