import { test, expect, Page } from '@playwright/test';

/**
 * End-to-End Tests for Agentic Integration Workflow
 * Tests the complete sequence: User → MCP Agent → Knowledge Graph → External APIs → Context Store
 */

class AgenticWorkflowPage {
  constructor(private page: Page) {}

  // Navigation helpers
  async navigateToChat() {
    await this.page.click('[data-testid="nav-chat"]');
    await this.page.waitForSelector('[data-testid="mcp-chat-interface"]');
  }

  async navigateToKnowledgeGraph() {
    await this.page.click('[data-testid="nav-knowledge"]');
    await this.page.waitForSelector('[data-testid="knowledge-graph"]');
  }

  async navigateToDashboard() {
    await this.page.click('[data-testid="nav-dashboard"]');
    await this.page.waitForSelector('[data-testid="dashboard"]');
  }

  // Chat interaction helpers
  async startNewConversation() {
    await this.page.click('[data-testid="new-conversation-btn"]');
    await this.page.waitForSelector('[data-testid="chat-input"]');
  }

  async sendMessage(message: string) {
    await this.page.fill('[data-testid="chat-input"]', message);
    await this.page.click('[data-testid="send-message-btn"]');
  }

  async waitForAgentResponse() {
    await this.page.waitForSelector('[data-testid="agent-message"]:last-child', {
      timeout: 30000
    });
  }

  async getLastAgentMessage() {
    return await this.page.textContent('[data-testid="agent-message"]:last-child');
  }

  // Verification helpers
  async verifyIntegrationInDashboard(integrationName: string) {
    await this.navigateToDashboard();
    await this.page.waitForSelector(`[data-testid="integration-card"][data-name="${integrationName}"]`);
  }

  async verifyNotification(type: string, message: string) {
    await this.page.click('[data-testid="notifications-bell"]');
    await this.page.waitForSelector('[data-testid="notification-dropdown"]');
    
    const notification = this.page.locator(`[data-testid="notification"][data-type="${type}"]`);
    await expect(notification).toContainText(message);
  }
}

test.describe('Agentic Integration Workflow', () => {
  let workflowPage: AgenticWorkflowPage;

  test.beforeEach(async ({ page }) => {
    workflowPage = new AgenticWorkflowPage(page);
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
  });

  test('Complete Salesforce to Billing System Integration Workflow', async ({ page }) => {
    // Step 1: Navigate to MCP Agent Chat
    await workflowPage.navigateToChat();
    
    // Step 2: Start new conversation
    await workflowPage.startNewConversation();
    
    // Step 3: Send initial integration request
    await test.step('Send initial request: "Connect Salesforce to our billing system"', async () => {
      await workflowPage.sendMessage('Connect Salesforce to our billing system');
      await workflowPage.waitForAgentResponse();
      
      const response = await workflowPage.getLastAgentMessage();
      expect(response).toContain('Salesforce');
      expect(response).toContain('billing');
    });

    // Step 4: Verify Knowledge Graph queries (check network requests)
    await test.step('Verify Knowledge Graph integration', async () => {
      // Monitor API calls to knowledge graph
      const kgRequests = [];
      page.on('request', request => {
        if (request.url().includes('/api/v1/knowledge/')) {
          kgRequests.push(request.url());
        }
      });

      // Navigate to Knowledge Graph to verify data
      await workflowPage.navigateToKnowledgeGraph();
      
      // Search for Salesforce patterns
      await page.fill('[data-testid="kg-search-input"]', 'Salesforce billing');
      await page.click('[data-testid="kg-search-btn"]');
      
      // Verify search results
      await page.waitForSelector('[data-testid="kg-search-results"]');
      const results = await page.locator('[data-testid="kg-result-item"]').count();
      expect(results).toBeGreaterThan(0);
    });

    // Step 5: Return to chat and verify integration plan
    await test.step('Verify integration plan presentation', async () => {
      await workflowPage.navigateToChat();
      
      // Wait for plan to be presented
      await page.waitForSelector('[data-testid="integration-plan"]', { timeout: 30000 });
      
      const plan = await page.textContent('[data-testid="integration-plan"]');
      expect(plan).toContain('data flow');
      expect(plan).toContain('field mapping');
      expect(plan).toContain('sync frequency');
    });

    // Step 6: Request modification for tax calculations
    await test.step('Request modification: "Modify to include tax calculations"', async () => {
      await workflowPage.sendMessage('Modify to include tax calculations');
      await workflowPage.waitForAgentResponse();
      
      const response = await workflowPage.getLastAgentMessage();
      expect(response).toContain('tax');
      expect(response).toContain('calculation');
    });

    // Step 7: Verify updated plan includes tax logic
    await test.step('Verify updated plan with tax calculations', async () => {
      await page.waitForSelector('[data-testid="updated-integration-plan"]', { timeout: 30000 });
      
      const updatedPlan = await page.textContent('[data-testid="updated-integration-plan"]');
      expect(updatedPlan).toContain('tax calculation');
      expect(updatedPlan).toContain('tax logic');
    });

    // Step 8: Approve and deploy integration
    await test.step('Approve and deploy: "Approve and deploy"', async () => {
      await workflowPage.sendMessage('Approve and deploy');
      await workflowPage.waitForAgentResponse();
      
      const response = await workflowPage.getLastAgentMessage();
      expect(response).toContain('deploy');
      expect(response).toContain('approved');
    });

    // Step 9: Verify integration appears in dashboard
    await test.step('Verify integration in dashboard', async () => {
      await workflowPage.verifyIntegrationInDashboard('Salesforce to Billing System');
      
      // Check integration status
      const status = await page.textContent('[data-testid="integration-status"]');
      expect(['deploying', 'active', 'deployed']).toContain(status?.toLowerCase());
    });

    // Step 10: Verify notifications
    await test.step('Verify success notifications', async () => {
      await workflowPage.verifyNotification('success', 'Integration deployed');
    });
  });

  test('Error Handling: Unknown System Integration', async ({ page }) => {
    await workflowPage.navigateToChat();
    await workflowPage.startNewConversation();
    
    // Test with unknown system
    await workflowPage.sendMessage('Connect UnknownSystem to our billing system');
    await workflowPage.waitForAgentResponse();
    
    const response = await workflowPage.getLastAgentMessage();
    expect(response).toContain('unknown');
    expect(response).toContain('similar');
  });

  test('Iterative Refinement Workflow', async ({ page }) => {
    await workflowPage.navigateToChat();
    await workflowPage.startNewConversation();
    
    // Initial request
    await workflowPage.sendMessage('Connect Stripe to QuickBooks');
    await workflowPage.waitForAgentResponse();
    
    // First modification
    await workflowPage.sendMessage('Actually, make it sync only successful payments');
    await workflowPage.waitForAgentResponse();
    
    // Second modification
    await workflowPage.sendMessage('Add currency conversion for international payments');
    await workflowPage.waitForAgentResponse();
    
    // Third modification
    await workflowPage.sendMessage('Include refund handling');
    await workflowPage.waitForAgentResponse();
    
    // Verify final plan includes all modifications
    const finalPlan = await workflowPage.getLastAgentMessage();
    expect(finalPlan).toContain('successful payments');
    expect(finalPlan).toContain('currency conversion');
    expect(finalPlan).toContain('refund handling');
  });

  test('Search Functionality Integration', async ({ page }) => {
    // Test global search (Cmd+K)
    await page.keyboard.press('Meta+k'); // Mac
    await page.waitForSelector('[data-testid="search-modal"]');
    
    // Search for Salesforce
    await page.fill('[data-testid="search-input"]', 'Salesforce billing');
    
    // Verify both integration and knowledge results
    await page.waitForSelector('[data-testid="search-results"]');
    
    const integrationResults = await page.locator('[data-testid="integration-result"]').count();
    const knowledgeResults = await page.locator('[data-testid="knowledge-result"]').count();
    
    expect(integrationResults + knowledgeResults).toBeGreaterThan(0);
  });

  test('Real-time Updates During Integration Process', async ({ page }) => {
    // Open dashboard in background
    await workflowPage.navigateToDashboard();
    const initialIntegrationCount = await page.locator('[data-testid="integration-card"]').count();
    
    // Start integration process in chat
    await workflowPage.navigateToChat();
    await workflowPage.startNewConversation();
    await workflowPage.sendMessage('Connect Salesforce to our billing system');
    await workflowPage.waitForAgentResponse();
    await workflowPage.sendMessage('Approve and deploy');
    await workflowPage.waitForAgentResponse();
    
    // Return to dashboard and verify new integration appears
    await workflowPage.navigateToDashboard();
    
    // Wait for real-time update
    await page.waitForFunction(
      (expectedCount) => {
        const cards = document.querySelectorAll('[data-testid="integration-card"]');
        return cards.length > expectedCount;
      },
      initialIntegrationCount,
      { timeout: 30000 }
    );
    
    const finalIntegrationCount = await page.locator('[data-testid="integration-card"]').count();
    expect(finalIntegrationCount).toBeGreaterThan(initialIntegrationCount);
  });
});

test.describe('Performance Tests', () => {
  test('Response Time Benchmarks', async ({ page }) => {
    const workflowPage = new AgenticWorkflowPage(page);
    await page.goto('http://localhost:3001');
    
    // Measure chat response time
    await workflowPage.navigateToChat();
    await workflowPage.startNewConversation();
    
    const startTime = Date.now();
    await workflowPage.sendMessage('Connect Salesforce to billing system');
    await workflowPage.waitForAgentResponse();
    const responseTime = Date.now() - startTime;
    
    // Response should be under 10 seconds
    expect(responseTime).toBeLessThan(10000);
    
    console.log(`MCP Agent response time: ${responseTime}ms`);
  });
});

test.describe('Accessibility Tests', () => {
  test('Keyboard Navigation', async ({ page }) => {
    await page.goto('http://localhost:3001');
    
    // Test tab navigation through main interface
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Verify focus is visible
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });
});
