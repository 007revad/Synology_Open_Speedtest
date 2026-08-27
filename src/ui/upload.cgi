#!/bin/bash
# Read and discard upload data
cat > /dev/null
echo "Content-Type: text/plain"
echo "Access-Control-Allow-Origin: *"
echo "Access-Control-Allow-Methods: POST"
echo ""
echo "OK"
