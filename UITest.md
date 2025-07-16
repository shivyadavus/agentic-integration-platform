# Agentic Integration Platform - UI Testing Guide

## Overview
This guide walks you through testing the complete agentic integration workflow in the UI, following the sequence:
**User Request → MCP Agent → Knowledge Graph → External API Testing → Plan Presentation → Modifications → Deployment**

## Prerequisites
- Frontend running on: http://localhost:3001
- Backend running on: http://localhost:8000
- All services (PostgreSQL, Redis, Neo4j, Qdrant) running via `make dev`

## Test Workflow: "Connect Salesforce to Billing System"

### Step 1: Access the MCP Agent Chat Interface

1. **Navigate to AI Assistant**
   - Open http://localhost:3001
   - Click on **"AI Assistant"** in the left sidebar (chat bubble icon)
   - You should see the MCP Chat interface with conversation history

2. **Start New Conversation**
   - Click **"New Conversation"** button (+ icon)
   - The system will create a new conversation session

### Step 2: Initial Integration Request

1. **Send Natural Language Request**
   ```
   Type: "Connect Salesforce to our billing system"
   ```
   - Press Enter or click Send
   - The MCP Agent will process your request

2. **Expected Backend Actions** (visible in logs)
   - MCP Agent queries Context Store for previous Salesforce integrations
   - Knowledge Graph search for Salesforce schema and billing patterns
   - Semantic mappings retrieved and processed

3. **Expected UI Response**
   - Loading indicator while processing
   - Agent response with initial analysis
   - Suggested actions or follow-up questions

### Step 3: Knowledge Graph Integration

1. **Verify Knowledge Graph Query**
   - Switch to **"Knowledge Graph"** tab in sidebar
   - Search for "Salesforce" in the search box
   - You should see related patterns and schemas
   - Look for billing system integrations

2. **Check Semantic Mappings**
   - In Knowledge Graph, search for "billing patterns"
   - Verify that relevant integration patterns appear
   - Check that field mappings are suggested

### Step 4: External API Testing

1. **API Connectivity Check**
   - The MCP Agent should automatically test API connectivity
   - Look for status indicators in the chat response
   - Check for API capability summaries

2. **Integration Plan Presentation**
   - Agent should present a detailed integration plan
   - Plan should include:
     - Data flow diagram
     - Field mappings
     - Sync frequency options
     - Error handling approach

### Step 5: Plan Modification Request

1. **Request Modification**
   ```
   Type: "Modify to include tax calculations"
   ```
   - Send this follow-up message
   - Agent should acknowledge the modification request

2. **Expected Processing**
   - Context Store updated with modification request
   - Knowledge Graph queried for tax calculation patterns
   - Updated plan generated

3. **Verify Updated Plan**
   - New plan should include tax calculation logic
   - Additional field mappings for tax data
   - Updated data flow including tax processing

### Step 6: Final Approval and Deployment

1. **Approve Integration**
   ```
   Type: "Approve and deploy"
   ```
   - Send approval message
   - Agent should confirm deployment initiation

2. **Monitor Deployment**
   - Switch to **"Dashboard"** view
   - Check for new integration in the list
   - Status should show "deploying" then "active"

3. **Verify Final State**
   - Integration should appear in dashboard
   - Status indicators should be green/active
   - Deployment logs should be available

## Alternative Testing Paths

### Using Integration Wizard

1. **Access Integration Wizard**
   - Click **"Create Integration"** in sidebar
   - Follow the step-by-step wizard

2. **Natural Language Input**
   - Enter: "Connect Salesforce to our billing system with tax calculations"
   - Proceed through wizard steps
   - Compare results with chat-based approach

### Using Search Functionality

1. **Global Search Test**
   - Press `Cmd+K` (Mac) or `Ctrl+K` (Windows/Linux)
   - Search for "Salesforce billing"
   - Verify both integrations and knowledge results appear

2. **Knowledge-Specific Search**
   - In Knowledge Graph view
   - Use semantic search for integration patterns
   - Test pattern discovery and recommendations

## Notification Testing

1. **Bell Icon Functionality**
   - Click the bell icon in header
   - Verify notifications appear for:
     - Integration creation
     - Plan generation
     - Deployment completion
     - Any errors or warnings

2. **Real-time Updates**
   - Keep dashboard open during integration process
   - Verify real-time status updates
   - Check notification badges update correctly

## Expected API Endpoints Hit

During the workflow, these endpoints should be called:

1. **MCP Agent Endpoints**
   - `POST /api/v1/mcp/conversations` - Start conversation
   - `POST /api/v1/mcp/conversations/{id}/messages` - Send messages
   - `POST /api/v1/mcp/conversations/{id}/context` - Retrieve context
   - `POST /api/v1/mcp/conversations/{id}/plan` - Generate plan
   - `POST /api/v1/mcp/conversations/{id}/approve` - Approve integration

2. **Knowledge Graph Endpoints**
   - `POST /api/v1/knowledge/patterns/search` - Search patterns
   - `POST /api/v1/knowledge/semantic/search` - Semantic search
   - `POST /api/v1/knowledge/schemas/query` - Query schemas

3. **Integration Endpoints**
   - `GET /api/v1/integrations/` - List integrations
   - `POST /api/v1/integrations/` - Create integration
   - `POST /api/v1/integrations/{id}/plan` - Generate plan
   - `POST /api/v1/integrations/{id}/deploy` - Deploy integration

## Troubleshooting

### Common Issues

1. **MCP Agent Not Responding**
   - Check backend logs for errors
   - Verify OpenAI API key is configured
   - Ensure all services are running

2. **Knowledge Graph Empty**
   - Check Neo4j connection
   - Verify sample data is loaded
   - Check Qdrant vector database

3. **API Connectivity Issues**
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Ensure database migrations are complete

### Debug Steps

1. **Check Browser Console**
   - Open Developer Tools (F12)
   - Look for JavaScript errors
   - Check network requests

2. **Backend Logs**
   - Monitor terminal running `make dev`
   - Look for API request logs
   - Check for database connection issues

3. **Database Verification**
   - Check PostgreSQL for integration records
   - Verify Neo4j has knowledge graph data
   - Ensure Redis is caching properly

## Success Criteria

✅ **Complete Workflow Success**
- User can input natural language request
- MCP Agent processes and responds intelligently
- Knowledge Graph provides relevant patterns
- Integration plan is generated and modifiable
- Final deployment creates working integration
- All UI components respond correctly
- Notifications work properly
- Search functionality operates as expected

## Performance Expectations

- Initial response: < 3 seconds
- Knowledge Graph queries: < 2 seconds
- Plan generation: < 5 seconds
- Deployment initiation: < 2 seconds
- UI updates: Real-time (< 1 second)

## Advanced Testing Scenarios

### Scenario 1: Complex Multi-System Integration
```
Test Input: "Create a workflow that syncs Salesforce leads to HubSpot, then sends new contacts to our email marketing platform, and finally updates our billing system when deals close"
```

**Expected Behavior:**
- MCP Agent breaks down into multiple integration steps
- Knowledge Graph provides patterns for each system pair
- Plan includes data flow between all systems
- Error handling for each integration point

### Scenario 2: Error Handling and Recovery
```
Test Input: "Connect to a system that doesn't exist in our knowledge base"
```

**Expected Behavior:**
- Agent gracefully handles unknown systems
- Suggests similar known systems
- Asks clarifying questions
- Provides fallback options

### Scenario 3: Iterative Refinement
```
Test Sequence:
1. "Connect Stripe to QuickBooks"
2. "Actually, make it sync only successful payments"
3. "Add currency conversion for international payments"
4. "Include refund handling"
```

**Expected Behavior:**
- Each modification builds on previous context
- Plan updates incrementally
- Previous decisions are preserved
- Context Store maintains conversation history

## UI Component Testing Checklist

### Header Components
- [ ] Search icon opens modal (click + Cmd/Ctrl+K)
- [ ] Bell icon shows notifications dropdown
- [ ] Theme toggle works correctly
- [ ] User profile menu accessible
- [ ] Status indicators show system health

### Sidebar Navigation
- [ ] All navigation items clickable
- [ ] Active state highlights correctly
- [ ] Smooth transitions between views
- [ ] Responsive design on mobile
- [ ] Icons and labels display properly

### Dashboard View
- [ ] Integration cards display correctly
- [ ] Status indicators accurate
- [ ] Real-time updates work
- [ ] Charts and metrics load
- [ ] Quick actions functional

### MCP Chat Interface
- [ ] Message input responsive
- [ ] Conversation history persists
- [ ] Loading states during processing
- [ ] Error messages display clearly
- [ ] Suggested actions clickable
- [ ] File attachments (if supported)
- [ ] Message timestamps accurate

### Integration Wizard
- [ ] Step progression works
- [ ] Form validation active
- [ ] Preview functionality
- [ ] Back/forward navigation
- [ ] Save draft capability
- [ ] Integration with MCP Agent

### Knowledge Graph View
- [ ] Graph visualization renders
- [ ] Node interactions work
- [ ] Search filters results
- [ ] Zoom and pan controls
- [ ] Entity details on hover/click
- [ ] Export functionality

## API Integration Testing

### Test API Responses
Use browser dev tools or curl to verify:

```bash
# Test MCP conversation start
curl -X POST http://localhost:8000/api/v1/mcp/conversations \
  -H "Content-Type: application/json" \
  -d '{"initial_request": "Connect Salesforce to billing system"}'

# Test knowledge search
curl -X POST http://localhost:8000/api/v1/knowledge/semantic/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Salesforce billing integration"}'

# Test integration creation
curl -X POST http://localhost:8000/api/v1/integrations/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Integration", "natural_language_spec": "Test spec"}'
```

### Error Scenarios to Test
1. **Network Failures**
   - Disconnect internet during operation
   - Verify graceful error handling
   - Check retry mechanisms

2. **Backend Service Down**
   - Stop backend service
   - Verify UI shows appropriate errors
   - Test fallback to cached data

3. **Invalid Input Handling**
   - Send malformed requests
   - Test input validation
   - Verify error messages are user-friendly

## Performance Testing

### Load Testing Steps
1. **Multiple Conversations**
   - Open several chat sessions
   - Send concurrent requests
   - Monitor response times

2. **Large Knowledge Queries**
   - Search for broad terms
   - Test pagination
   - Verify memory usage

3. **Real-time Updates**
   - Create multiple integrations
   - Monitor dashboard updates
   - Check notification performance

## Accessibility Testing

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Enter/Space activate buttons
- [ ] Escape closes modals
- [ ] Arrow keys navigate lists

### Screen Reader Support
- [ ] Alt text on images
- [ ] ARIA labels on complex components
- [ ] Proper heading hierarchy
- [ ] Form labels associated correctly

### Visual Accessibility
- [ ] Sufficient color contrast
- [ ] Text scalable to 200%
- [ ] Focus indicators visible
- [ ] No color-only information

## Mobile Responsiveness

### Test on Different Screen Sizes
- [ ] Mobile phones (320px-480px)
- [ ] Tablets (768px-1024px)
- [ ] Desktop (1200px+)
- [ ] Touch interactions work
- [ ] Scrolling smooth on mobile

---

**Note**: This comprehensive testing guide ensures the full agentic integration paradigm works seamlessly across all user interfaces and interaction patterns. The workflow demonstrates how natural language can drive complex B2B software integrations through AI-powered agents and knowledge systems.
