#!/usr/bin/env bash
set -euo pipefail

read -r -p "Create new schema mastr-erwartung.yml? [y/N] " create_schema
if [[ "$create_schema" =~ ^[Yy]$ ]]; then
    linkml-map derive-schema -T mastr-map.yml ../../schema/TC57CIM-reduced.yml > mastr-erwartung.yml
    echo "Created mastr-erwartung.yml"
fi

echo ""
echo "Generate validation files:"
echo "  1) SHACL (shacl.ttl)"
echo "  2) SQL validation (validation.sql)"
echo "  3) Both"
echo "  0) Skip"
read -r -p "Choice [0-3]: " gen_choice

if [[ "$gen_choice" == "1" || "$gen_choice" == "3" ]]; then
    linkml generate shacl mastr-erwartung.yml > shacl.ttl
    echo "Created shacl.ttl"
fi

if [[ "$gen_choice" == "2" || "$gen_choice" == "3" ]]; then
    linkml generate sqlvalidation mastr-erwartung.yml > validation.sql
    echo "Created validation.sql"
fi
