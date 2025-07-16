import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for Playwright tests
 * Ensures the application is ready before running tests
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for Agentic Integration Platform tests...');
  
  // Launch browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for frontend to be ready
    console.log('⏳ Waiting for frontend to be ready...');
    await page.goto('http://localhost:3001', { waitUntil: 'networkidle' });
    await page.waitForSelector('[data-testid="app-ready"]', { timeout: 60000 });
    console.log('✅ Frontend is ready');
    
    // Wait for backend to be ready
    console.log('⏳ Waiting for backend to be ready...');
    const healthResponse = await page.request.get('http://localhost:8000/health');
    if (!healthResponse.ok()) {
      throw new Error('Backend health check failed');
    }
    console.log('✅ Backend is ready');
    
    // Verify database connections
    console.log('⏳ Verifying database connections...');
    const integrationsResponse = await page.request.get('http://localhost:8000/api/v1/integrations/');
    if (!integrationsResponse.ok()) {
      throw new Error('Database connection failed');
    }
    console.log('✅ Database connections verified');
    
    // Seed test data if needed
    console.log('⏳ Seeding test data...');
    await seedTestData(page);
    console.log('✅ Test data seeded');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('🎉 Global setup completed successfully!');
}

async function seedTestData(page: any) {
  // Create sample integration for testing
  const sampleIntegration = {
    name: 'Test Salesforce Integration',
    natural_language_spec: 'Sample integration for testing purposes',
    status: 'active',
    integration_type: 'sync'
  };
  
  try {
    await page.request.post('http://localhost:8000/api/v1/integrations/', {
      data: sampleIntegration
    });
  } catch (error) {
    // Integration might already exist, which is fine
    console.log('Sample integration already exists or creation failed:', error.message);
  }
  
  // Add sample knowledge graph data
  try {
    await page.request.post('http://localhost:8000/api/v1/knowledge/entities', {
      data: {
        entity_type: 'system',
        properties: {
          name: 'Salesforce',
          type: 'CRM',
          api_version: 'v52.0'
        }
      }
    });
  } catch (error) {
    console.log('Sample knowledge entity already exists or creation failed:', error.message);
  }
}

export default globalSetup;
