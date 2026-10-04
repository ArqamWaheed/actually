#!/usr/bin/env bash
# Sends a few real plan requests so Sentry has traces to inspect. Usage: scripts/sentry_demo_traffic.sh <n>
for i in $(seq 1 "${1:-3}"); do
  curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" -X POST localhost:8000/api/plan -H 'Content-Type: application/json' \
    -d '{"text":"ok so today: submit os lab (20 min), call nani back, buy charger, revise dbms ch 3 for an hour, reply to the group chat abt the presentation which i am avoiding","free_min":150,"profile":"demo"}'
done
