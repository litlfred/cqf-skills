#!/usr/bin/env bash
# What clinical-reasoning 4.13.0's CDS Hooks service (cqf-fhir-cr-hapi, HAPI FHIR 8.12.0) makes of a
# PlanDefinition, on a folder in IG layout (input/resources, input/tests, input/vocabulary).
#
# Usage: scripts/encode/run.sh PROJECT discovery PLAN_DEFINITION_ID
#        scripts/encode/run.sh PROJECT response PLAN_DEFINITION_ID Patient/<id>
#        scripts/encode/run.sh PROJECT apply PLAN_DEFINITION_ID Patient/<id>
#   discovery prints the discovery document for that PlanDefinition; response runs $r5.apply (as the R4 service does) and prints
#   the CDS Hooks response it encodes; apply prints the $r5.apply result. ENCODE_TRACE=1 adds stack traces.
# Needs Java 17+ and Maven. The first run downloads the dependencies (about 320 MB) into scripts/encode/lib/.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
if [[ ! -d "$here/lib" ]]; then
  (cd "$here" && mvn -q dependency:copy-dependencies -DoutputDirectory=lib)
fi
sep=":"; jhere="$here"
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) sep=";"; jhere="$(cygpath -w "$here")" ;; esac
cp="$jhere/out"
for j in "$here"/lib/*.jar; do cp="$cp$sep$jhere/lib/$(basename "$j")"; done
if [[ ! -f "$here/out/Encode.class" || "$here/Encode.java" -nt "$here/out/Encode.class" ]]; then
  mkdir -p "$here/out"
  javac -d "$jhere/out" -cp "$cp" "$jhere/Encode.java"
fi
java -Dorg.slf4j.simpleLogger.defaultLogLevel=warn -Dlogback.configurationFile="$jhere/logback.xml" -cp "$cp" Encode "$@"
