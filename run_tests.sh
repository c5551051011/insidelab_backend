#!/bin/bash
#
# Test runner script for InsideLab backend
# This script sets up the proper environment and runs tests
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  InsideLab Backend Test Runner${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Set test environment
export DJANGO_SETTINGS_MODULE=insidelab.settings.test

# Function to run specific test
run_test() {
    local test_path=$1
    local test_name=$2

    echo -e "${YELLOW}Running ${test_name}...${NC}"
    python manage.py test $test_path --verbosity=2

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${test_name} passed${NC}"
        echo ""
    else
        echo -e "${RED}✗ ${test_name} failed${NC}"
        echo ""
        return 1
    fi
}

# Parse command line arguments
TEST_SUITE=${1:-all}

case $TEST_SUITE in
    all)
        echo "Running all tests..."
        echo ""
        run_test "apps.authentication.tests" "Authentication Tests"
        run_test "apps.universities.tests" "Universities Tests"
        run_test "apps.labs.tests" "Labs Tests"
        run_test "apps.reviews.tests" "Reviews Tests"
        ;;
    auth|authentication)
        run_test "apps.authentication.tests" "Authentication Tests"
        ;;
    uni|universities)
        run_test "apps.universities.tests" "Universities Tests"
        ;;
    labs)
        run_test "apps.labs.tests" "Labs Tests"
        ;;
    reviews)
        run_test "apps.reviews.tests" "Reviews Tests"
        ;;
    models)
        echo "Running all model tests..."
        echo ""
        run_test "apps.authentication.tests.test_models" "Authentication Model Tests"
        run_test "apps.universities.tests.test_models" "Universities Model Tests"
        run_test "apps.labs.tests.test_models" "Labs Model Tests"
        run_test "apps.reviews.tests.test_models" "Reviews Model Tests"
        ;;
    views)
        echo "Running all view tests..."
        echo ""
        run_test "apps.authentication.tests.test_views" "Authentication View Tests"
        ;;
    *)
        # Run specific test path
        echo "Running custom test: $TEST_SUITE"
        python manage.py test $TEST_SUITE --verbosity=2
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  All tests completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
else
    echo ""
    echo -e "${RED}=====================================${NC}"
    echo -e "${RED}  Some tests failed${NC}"
    echo -e "${RED}=====================================${NC}"
    exit 1
fi
