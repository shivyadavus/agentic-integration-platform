# Development Sample Data

The Agentic Integration Platform automatically loads realistic sample data when developers run `make dev`. This provides a rich, enterprise-grade knowledge graph for development and testing.

## 🚀 Quick Start

When you run the development environment, sample data is automatically loaded:

```bash
make dev
```

This will:
1. Start all required services (PostgreSQL, Redis, Neo4j, Qdrant)
2. Wait for databases to be ready
3. **Automatically load realistic sample data**
4. Start the API server

## 📊 Sample Data Overview

The system loads **18 realistic entities** across 4 main types:

### 🏢 Systems (6 entities)
Real enterprise platforms with detailed specifications:

- **Salesforce Sales Cloud** - Enterprise CRM managing 50M+ records
- **QuickBooks Enterprise** - Accounting software handling $2B+ transactions
- **Stripe Connect** - Global payment infrastructure processing $640B+ annually
- **HubSpot Marketing Hub Enterprise** - Marketing platform with 100M+ contacts
- **Microsoft Dynamics 365** - Enterprise business applications suite
- **NetSuite ERP** - Cloud ERP for 31,000+ organizations

### 🔌 API Endpoints (4 entities)
Production-grade APIs with real specifications:

- **Salesforce REST API v58.0** - Handling 1B+ API calls daily
- **QuickBooks Online API v3** - Processing millions of financial transactions
- **Stripe Payments API v1** - 99.99% uptime, sub-second response times
- **HubSpot CRM API v3** - Managing 100M+ contacts with real-time sync

### 🔄 Integration Patterns (5 entities)
Real-world integration scenarios:

- **Quote-to-Cash Automation** - End-to-end revenue process (40% faster sales cycle)
- **Customer 360 Data Unification** - Master data management across 15+ systems
- **Order-to-Cash Integration** - Complete order processing workflow
- **Lead Nurturing Workflow** - Marketing automation with progressive scoring
- **Financial Reporting Aggregation** - Multi-source financial data consolidation

### 🏗️ Business Objects (3 entities)
Enterprise data entities:

- **Enterprise Customer Record** - Unified customer entity (50M+ records)
- **Invoice** - Financial document with transactional data
- **Product** - Master data for goods and services

## 🎯 Realistic Data Features

All sample data includes:

### **Detailed Properties**
- Vendor information and categories
- API versions and authentication methods
- Rate limits and compliance standards
- Pricing models and complexity ratings
- Business impact metrics and ROI data

### **Enterprise Specifications**
- Real-world transaction volumes
- Actual compliance certifications (SOC 2, GDPR, PCI DSS)
- Production deployment models
- Integration complexity assessments
- Success rates and implementation timelines

### **Business Context**
- Typical use cases and scenarios
- Common challenges and solutions
- Best practices and recommendations
- Key performance indicators
- Data quality scores and governance rules

## 🛠️ Development Commands

### Standard Development (with sample data)
```bash
make dev
```
Starts environment and loads sample data automatically.

### Clean Development (no sample data)
```bash
make dev-clean
```
Starts environment without loading sample data.

### Load Sample Data Only
```bash
make dev-data
```
Loads sample data into existing environment.

### Stop Development Environment
```bash
make dev-down
```
Stops all services and containers.

## 🔧 Customization

### Adding New Sample Data

To add new entities, edit `scripts/init_dev_data.py`:

```python
# Add to sample_entities list
{
    "name": "Your System Name",
    "entity_type": "system",  # or "api_endpoint", "pattern", "business_object"
    "properties": {
        "name": "Your System Name",
        "vendor": "Vendor Name",
        "category": "System Category",
        # ... add realistic properties
    }
}
```

### Modifying Existing Data

The script automatically refreshes data on each run, so you can:
1. Edit the properties in `scripts/init_dev_data.py`
2. Run `make dev-data` to reload
3. Changes will be reflected immediately

## 📈 Knowledge Graph Visualization

The sample data creates a rich knowledge graph that demonstrates:

- **System-to-API relationships** (HAS_API)
- **Pattern-to-System mappings** (APPLIES_TO)
- **Business Object storage** (STORED_IN)
- **Pattern dependencies** (ENABLES, FEEDS_INTO)

This provides a realistic foundation for:
- Testing integration recommendations
- Demonstrating AI-powered suggestions
- Validating knowledge graph queries
- Showcasing the complete platform capabilities

## 🎉 Benefits for Developers

### **Immediate Productivity**
- No manual data setup required
- Rich, realistic data from day one
- Comprehensive test scenarios available

### **Realistic Testing**
- Enterprise-grade data volumes
- Real-world integration patterns
- Production-like API specifications

### **Demo-Ready Environment**
- Professional sample data
- Complete integration scenarios
- Impressive knowledge graph visualization

## 🔍 Troubleshooting

### Data Not Loading
If sample data doesn't load automatically:

```bash
# Check if API server is running
curl http://localhost:8000/api/v1/knowledge/entities

# Manually load data
make dev-data

# Check logs for errors
docker-compose logs -f
```

### Refreshing Data
To refresh with latest sample data:

```bash
make dev-down
make dev
```

This ensures you always have the most current realistic sample data for development and testing.

---

**Ready to develop with enterprise-grade sample data!** 🚀
