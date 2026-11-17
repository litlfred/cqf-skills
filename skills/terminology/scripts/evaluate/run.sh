#!/usr/bin/env bash
# Run Library $evaluate with clinical-reasoning 4.13.0 on a folder in IG layout (input/resources,
# input/tests, input/vocabulary), and print the result (one parameter per definition) as JSON.
#
# Usage: scripts/evaluate/run.sh PROJECT LIBRARY_ID SUBJECT [MODE [EXPRESSION...]]
#   SUBJECT as Patient/<id>. MODE is the retrieve's terminology filter: auto (default), value-set-url,
#   inline-codes or in-memory. Each EXPRESSION is evaluated on its own run.
# Needs Java 17+ and Maven. The first run downloads the dependencies into scripts/evaluate/lib/.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
if [[ ! -d "$here/lib" ]]; then
  (cd "$here" && mvn -q dependency:copy-dependencies -DoutputDirectory=lib)
fi
sep=":"; jhere="$here"
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) sep=";"; jhere="$(cygpath -w "$here")" ;; esac
cp="$jhere/out"
for j in "$here"/lib/*.jar; do cp="$cp$sep$jhere/lib/$(basename "$j")"; done
if [[ ! -f "$here/out/Evaluate.class" || "$here/Evaluate.java" -nt "$here/out/Evaluate.class" ]]; then
  mkdir -p "$here/out"
  javac -d "$jhere/out" -cp "$cp" "$jhere/Evaluate.java"
fi
java -Dorg.slf4j.simpleLogger.defaultLogLevel=warn -cp "$cp" Evaluate "$@"
