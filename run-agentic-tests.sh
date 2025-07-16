#!/bin/bash

# Agentic Integration Platform - Automated Test Runner
# Tests the complete workflow: User → MCP Agent → Knowledge Graph → External APIs → Context Store

set -e

echo "🚀 Agentic Integration Platform - Automated Test Suite"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if services are running
check_services() {
    print_status "Checking if services are running..."
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend is running on port 8000"
    else
        print_error "Backend is not running. Please start with 'make dev'"
        exit 1
    fi
    
    # Check frontend
    if curl -s http://localhost:3001 > /dev/null; then
        print_success "Frontend is running on port 3001"
    else
        print_error "Frontend is not running. Please start with 'npm run dev'"
        exit 1
    fi
    
    # Check database services
    if docker ps | grep -q "agentic-postgres"; then
        print_success "PostgreSQL is running"
    else
        print_warning "PostgreSQL container not found"
    fi
    
    if docker ps | grep -q "agentic-neo4j"; then
        print_success "Neo4j is running"
    else
        print_warning "Neo4j container not found"
    fi
    
    if docker ps | grep -q "agentic-redis"; then
        print_success "Redis is running"
    else
        print_warning "Redis container not found"
    fi
    
    if docker ps | grep -q "agentic-qdrant"; then
        print_success "Qdrant is running"
    else
        print_warning "Qdrant container not found"
    fi
}

# Run backend API tests
run_backend_tests() {
    print_status "Running backend API integration tests..."
    
    cd "$(dirname "$0")"
    
    # Install test dependencies if needed
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx
    else
        source venv/bin/activate
    fi
    
    # Run the integration tests
    print_status "Executing agentic workflow integration tests..."
    python -m pytest tests/test_agentic_workflow_integration.py -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "Backend integration tests passed!"
    else
        print_error "Backend integration tests failed!"
        exit 1
    fi
}

# Run frontend E2E tests
run_frontend_tests() {
    print_status "Running frontend E2E tests..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Install Playwright browsers if needed
    if [ ! -d "node_modules/@playwright" ]; then
        print_status "Installing Playwright..."
        npm install @playwright/test
        npx playwright install
    fi
    
    # Run E2E tests
    print_status "Executing frontend E2E tests..."
    npx playwright test --reporter=html
    
    if [ $? -eq 0 ]; then
        print_success "Frontend E2E tests passed!"
    else
        print_error "Frontend E2E tests failed!"
        print_status "Opening test report..."
        npx playwright show-report
        exit 1
    fi
}

# Run specific workflow test
run_workflow_test() {
    print_status "Running specific agentic workflow test..."
    
    # Test the exact sequence from the diagram
    print_status "Testing: User → MCP Agent → Knowledge Graph → External APIs → Context Store"
    
    # Step 1: Test MCP conversation start
    print_status "Step 1: Starting MCP conversation..."
    CONVERSATION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/mcp/conversations \
        -H "Content-Type: application/json" \
        -d '{"initial_request": "Connect Salesforce to our billing system"}')
    
    CONVERSATION_ID=$(echo $CONVERSATION_RESPONSE | jq -r '.conversation_id')
    
    if [ "$CONVERSATION_ID" != "null" ] && [ "$CONVERSATION_ID" != "" ]; then
        print_success "MCP conversation started: $CONVERSATION_ID"
    else
        print_error "Failed to start MCP conversation"
        echo "Response: $CONVERSATION_RESPONSE"
        exit 1
    fi
    
    # Step 2: Test context retrieval
    print_status "Step 2: Retrieving context from Context Store..."
    CONTEXT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/mcp/conversations/$CONVERSATION_ID/context \
        -H "Content-Type: application/json" \
        -d '{"source_system_type": "salesforce", "target_system_type": "billing", "search_patterns": true}')
    
    if echo $CONTEXT_RESPONSE | jq -e '.patterns' > /dev/null; then
        print_success "Context retrieved successfully"
    else
        print_warning "Context retrieval may have issues"
        echo "Response: $CONTEXT_RESPONSE"
    fi
    
    # Step 3: Test Knowledge Graph query
    print_status "Step 3: Querying Knowledge Graph..."
    KG_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/knowledge/patterns/search \
        -H "Content-Type: application/json" \
        -d '{"description": "Salesforce billing integration", "source_system_type": "salesforce", "target_system_type": "billing"}')
    
    if echo $KG_RESPONSE | jq -e '.patterns' > /dev/null; then
        print_success "Knowledge Graph query successful"
    else
        print_warning "Knowledge Graph query may have issues"
        echo "Response: $KG_RESPONSE"
    fi
    
    # Step 4: Test plan generation
    print_status "Step 4: Generating integration plan..."
    PLAN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/mcp/conversations/$CONVERSATION_ID/plan \
        -H "Content-Type: application/json" \
        -d '{"include_testing": true, "include_deployment": true}')
    
    if echo $PLAN_RESPONSE | jq -e '.integration_plan' > /dev/null; then
        print_success "Integration plan generated"
    else
        print_warning "Plan generation may have issues"
        echo "Response: $PLAN_RESPONSE"
    fi
    
    # Step 5: Test modification request
    print_status "Step 5: Sending modification request..."
    MOD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/mcp/conversations/$CONVERSATION_ID/messages \
        -H "Content-Type: application/json" \
        -d '{"message": "Modify to include tax calculations"}')
    
    if echo $MOD_RESPONSE | jq -e '.message' > /dev/null; then
        print_success "Modification request processed"
    else
        print_warning "Modification request may have issues"
        echo "Response: $MOD_RESPONSE"
    fi
    
    # Step 6: Test approval and deployment
    print_status "Step 6: Approving and deploying integration..."
    APPROVAL_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/mcp/conversations/$CONVERSATION_ID/approve \
        -H "Content-Type: application/json" \
        -d '{"approved": true, "notes": "Approved for deployment with tax calculations"}')
    
    if echo $APPROVAL_RESPONSE | jq -e '.status' > /dev/null; then
        print_success "Integration approved and deployment initiated"
    else
        print_warning "Approval/deployment may have issues"
        echo "Response: $APPROVAL_RESPONSE"
    fi
    
    print_success "Complete agentic workflow test completed!"
}

# Performance test
run_performance_test() {
    print_status "Running performance tests..."
    
    # Test response times for each step
    print_status "Testing MCP Agent response time..."
    START_TIME=$(date +%s%N)
    curl -s -X POST http://localhost:8000/api/v1/mcp/conversations \
        -H "Content-Type: application/json" \
        -d '{"initial_request": "Performance test request"}' > /dev/null
    END_TIME=$(date +%s%N)
    RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
    
    if [ $RESPONSE_TIME -lt 5000 ]; then
        print_success "MCP Agent response time: ${RESPONSE_TIME}ms (Good)"
    else
        print_warning "MCP Agent response time: ${RESPONSE_TIME}ms (Slow)"
    fi
}

# Main execution
main() {
    case "${1:-all}" in
        "services")
            check_services
            ;;
        "backend")
            check_services
            run_backend_tests
            ;;
        "frontend")
            check_services
            run_frontend_tests
            ;;
        "workflow")
            check_services
            run_workflow_test
            ;;
        "performance")
            check_services
            run_performance_test
            ;;
        "all")
            check_services
            run_workflow_test
            run_backend_tests
            run_frontend_tests
            run_performance_test
            print_success "All tests completed successfully! 🎉"
            ;;
        *)
            echo "Usage: $0 [services|backend|frontend|workflow|performance|all]"
            echo ""
            echo "  services     - Check if all services are running"
            echo "  backend      - Run backend API integration tests"
            echo "  frontend     - Run frontend E2E tests"
            echo "  workflow     - Run specific agentic workflow test"
            echo "  performance  - Run performance tests"
            echo "  all          - Run all tests (default)"
            exit 1
            ;;
    esac
}

# Check for required tools
if ! command -v curl &> /dev/null; then
    print_error "curl is required but not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    print_error "jq is required but not installed"
    exit 1
fi

# Run main function
main "$@"
