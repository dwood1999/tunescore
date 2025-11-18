#!/bin/bash
# Test script to verify authentication fix for track upload

echo "=== TuneScore Authentication Test ==="
echo ""

# Test 1: Upload without authentication (should fail with clear message)
echo "Test 1: Attempting upload WITHOUT authentication..."
curl -X POST https://music.quilty.app/api/v1/tracks/upload \
  -F 'track_data={"title":"Test","artist_name":"Test Artist"}' \
  2>&1 | head -20
echo ""
echo "Expected: 401 with 'Authentication required' message"
echo ""

# Test 2: Test authentication endpoint
echo "Test 2: Checking health endpoint (no auth required)..."
curl -s https://music.quilty.app/api/v1/health | jq .
echo ""

# Test 3: Instructions for authenticated upload
echo "Test 3: To test WITH authentication:"
echo "1. Open https://music.quilty.app in your browser"
echo "2. Log in or register an account"
echo "3. Open browser DevTools (F12) -> Console"
echo "4. Check if token exists: localStorage.getItem('tunescore_access_token')"
echo "5. If token exists, try uploading a track from /upload page"
echo ""
echo "The upload should now work if you're logged in!"
echo "If you get 401, check:"
echo "  - You're logged in (token in localStorage)"
echo "  - Token hasn't expired"
echo "  - Frontend build is the latest version"

