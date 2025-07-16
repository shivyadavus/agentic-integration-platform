import { chromium, FullConfig } from '@playwright/test';

/**
 * Global teardown for Playwright tests
 * Cleans up test data and resources
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Clean up test data
    console.log('⏳ Cleaning up test data...');
    await cleanupTestData(page);
    console.log('✅ Test data cleaned up');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  } finally {
    await browser.close();
  }
  
  console.log('🎉 Global teardown completed!');
}

async function cleanupTestData(page: any) {
  try {
    // Get all integrations
    const integrationsResponse = await page.request.get('http://localhost:8000/api/v1/integrations/');
    if (integrationsResponse.ok()) {
      const integrations = await integrationsResponse.json();
      
      // Delete test integrations
      for (const integration of integrations) {
        if (integration.name.includes('Test') || integration.name.includes('Sample')) {
          try {
            await page.request.delete(`http://localhost:8000/api/v1/integrations/${integration.id}`);
          } catch (error) {
            console.log(`Failed to delete integration ${integration.id}:`, error.message);
          }
        }
      }
    }
  } catch (error) {
    console.log('Failed to cleanup integrations:', error.message);
  }
}

export default globalTeardown;
