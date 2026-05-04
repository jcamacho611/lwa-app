#!/bin/bash
# LWA Repo Health Check System
# Run this before any commit to ensure repo integrity

set -e  # Exit on any error

echo "🚀 LWA Repo Health Check"
echo "========================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Function to run check
run_check() {
    local name="$1"
    local command="$2"
    
    echo "📋 Checking: $name"
    if eval "$command" > /tmp/health-check.log 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}: $name"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $name"
        cat /tmp/health-check.log
        FAILED=1
        return 1
    fi
}

# Check 1: Git status
echo "1️⃣  Repository Status"
echo "--------------------"
run_check "Git status" "cd /Users/bdm/LWA/lwa-app && git status --short"
echo ""

# Check 2: Frontend dependencies
echo "2️⃣  Frontend Dependencies"
echo "------------------------"
if [ ! -d "lwa-web/node_modules" ]; then
    echo -e "${YELLOW}⚠️  WARNING${NC}: node_modules missing, running npm install..."
    run_check "npm install" "cd lwa-web && npm install"
else
    echo -e "${GREEN}✅${NC}: node_modules exists"
fi
echo ""

# Check 3: ESLint
echo "3️⃣  ESLint Check"
echo "----------------"
run_check "ESLint" "cd lwa-web && npm run lint"
echo ""

# Check 4: TypeScript
echo "4️⃣  TypeScript Check"
echo "--------------------"
run_check "TypeScript" "cd lwa-web && npm run type-check"
echo ""

# Check 5: Build
echo "5️⃣  Build Check"
echo "---------------"
run_check "Build" "cd lwa-web && npm run build"
echo ""

# Check 6: Python compilation
echo "6️⃣  Backend Python Check"
echo "------------------------"
run_check "Python compile" "cd lwa-backend && python3 -m compileall ."
echo ""

# Check 7: Backend imports
echo "7️⃣  Backend Dependencies"
echo "------------------------"
python3 - <<'PY' > /tmp/backend-imports.log 2>&1
import importlib.util
import sys

required = ["fastapi", "pydantic", "httpx", "uvicorn"]
missing = []

for name in required:
    if not importlib.util.find_spec(name):
        missing.append(name)

if missing:
    print(f"Missing: {', '.join(missing)}")
    sys.exit(1)
else:
    print("All core imports available")
PY

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: Backend core imports"
else
    echo -e "${RED}❌ FAIL${NC}: Backend core imports"
    cat /tmp/backend-imports.log
    FAILED=1
fi
echo ""

# Check 8: Offline smoke test
echo "8️⃣  Offline Fallback Test"
echo "-------------------------"
if [ -f "lwa-backend/test_offline.py" ]; then
    run_check "Offline test" "cd lwa-backend && python3 test_offline.py"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: test_offline.py not found (Phase 7 not complete)"
fi
echo ""

# Summary
echo "========================"
echo "📊 HEALTH CHECK SUMMARY"
echo "========================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "🎉 Repo is healthy and ready for commit!"
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "🔧 Fix the issues above before committing."
    exit 1
fi
