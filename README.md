# RiskRadar 🎯

**Internal BDR application for identifying GCs and asset owners after subcontractor incidents**

RiskRadar helps sales teams identify high-propensity opportunities by detecting subcontractor risk events and linking them to general contractors and asset owners who may need enhanced prequal and risk management solutions.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Make (optional, for convenience commands)

### Setup Instructions

1. **Clone and navigate to the project:**
   ```bash
   cd risk-radar
   ```

2. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

3. **Run the complete demo:**
   ```bash
   make demo
   ```

   This will:
   - Build all containers
   - Start the database and services
   - Seed with sample data
   - Launch the frontend

4. **Access the application:**
   - **Frontend:** http://localhost:3000
   - **API:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs

### Alternative Setup (Step by Step)

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Seed database with sample data
docker-compose exec api python seed_data.py
```

## 📊 Features

### Core Functionality
- **Data Ingestion**: Multi-source data collection from OSHA, news feeds, and ITA metrics
- **Entity Resolution**: Company name normalization and relationship mapping  
- **Risk Scoring**: Propensity scoring based on incident recency, severity, and patterns
- **Target Identification**: Automated opportunity generation for GCs/owners
- **Outreach Generation**: Empathetic, consultative messaging templates
- **PDF Export**: Professional prospect packs for sales teams

### User Interface
- **Dashboard**: Real-time incident tracking and opportunity overview
- **Target List**: Prioritized opportunities with filtering and sorting
- **Target Detail**: Deep-dive analysis with incident timelines and benchmarks
- **Outreach Kit**: Generated email, LinkedIn, and call templates
- **Admin Panel**: Data ingestion, file uploads, and configuration

## 🏗️ Architecture

### Backend (`/backend`)
- **FastAPI** REST API with automatic OpenAPI documentation
- **SQLModel** for database modeling and migrations
- **PostgreSQL** for primary data storage
- **Redis** for background task processing
- **Celery** for asynchronous data ingestion

### Frontend (`/frontend`)
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Mantine UI** for professional components
- **Recharts** for data visualizations

### Data Sources
- **OSHA Establishment Search**: Inspections and citations
- **OSHA Accident Reports**: Incident narratives and investigations
- **OSHA ITA Data**: Injury Tracking Application metrics
- **News/RSS Feeds**: Industry incident reporting
- **Manual CSV Uploads**: Company relationships and aliases

### Infrastructure (`/infra`)
- **Docker Compose** for local development
- **PostgreSQL 15** with optimized indexing
- **Redis 7** for caching and queues
- **Nginx** for reverse proxy (production)

## 📁 Project Structure

```
risk-radar/
├── backend/              # Python FastAPI application
│   ├── connectors/       # Data source adapters
│   ├── scoring/          # Propensity scoring logic
│   ├── config/           # Configuration files
│   ├── models.py         # Database models
│   ├── main.py          # FastAPI application
│   └── requirements.txt  # Python dependencies
├── frontend/             # React TypeScript application
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route components
│   │   ├── utils/        # Utilities and API client
│   │   └── types/        # TypeScript definitions
│   └── package.json      # Node.js dependencies
├── infra/                # Infrastructure configuration
│   ├── docker/           # Container configurations
│   └── postgres/         # Database initialization
├── samples/              # Sample CSV files
├── docs/                 # Documentation and diagrams
└── docker-compose.yml    # Development environment
```

## 🎯 Usage Examples

### Flow A: Post-Incident Opportunity
1. **Incident Detection**: OSHA inspection finds violations at ABC Construction
2. **Relationship Mapping**: ABC linked to MegaBuild GC on Downtown Office project
3. **Propensity Scoring**: MegaBuild scores 81 (recent + severe + multiple violations)
4. **Outreach Generation**: Creates empathetic email focusing on "post-incident prequal strengthening"
5. **Sales Execution**: BDR reaches out with consultative approach, no blame/sensationalizing

### Flow B: Portfolio Risk Analysis
1. **Batch Processing**: Ingest 90 days of OSHA and news data
2. **Pattern Recognition**: Identify GCs with multiple sub incidents
3. **Benchmarking**: Compare sub DART rates vs industry standards
4. **Opportunity Prioritization**: Rank by propensity score and relationship confidence
5. **Campaign Creation**: Generate targeted messaging for portfolio risk review

## 🔧 Development

### Available Commands

```bash
# Development
make dev          # Start development environment
make build        # Build all containers  
make seed         # Seed database with sample data
make demo         # Full demo setup

# Maintenance
make clean        # Remove containers and volumes
make logs         # View service logs
make db           # Access database shell
make shell        # Access API Python shell

# Testing & Quality
make test         # Run test suite
make lint         # Run code linting
```

### API Endpoints

#### Core Resources
- `GET /companies` - List companies with filtering
- `GET /events` - List incidents with filtering
- `GET /opportunities` - List target opportunities
- `POST /opportunities/rebuild` - Recalculate scores

#### Outreach
- `POST /outreach/generate` - Generate outreach kit
- `GET /outreach/{id}` - Get outreach templates
- `POST /outreach/{id}/export/pdf` - Export prospect pack

#### Data Management
- `POST /ingest/run` - Run data ingestion
- `POST /uploads/sub_relationships` - Upload relationship CSV
- `POST /uploads/company_aliases` - Upload aliases CSV

### Database Schema

Key tables:
- `companies` - GCs, owners, and subcontractors
- `events` - Safety incidents and violations
- `target_opportunities` - Scored opportunities
- `outreach_kits` - Generated messaging
- `sub_relationships` - Project-based connections

## 📈 Scoring Methodology

Propensity scores (0-100) are calculated using weighted factors:

- **Incident Recency (30%)**: Exponential decay over 180 days
- **Incident Severity (25%)**: Fatalities, citations, penalties
- **Frequency (15%)**: Multiple incidents in 24 months
- **ITA Metrics (15%)**: DART rate vs industry benchmarks
- **Trade Risk (5%)**: High-risk activities (steel, roofing, excavation)
- **Relationship Certainty (5%)**: Confidence in GC-sub connection
- **News Coverage (5%)**: Negative media attention

### Benchmark Configuration

DART rate benchmarks by NAICS code are configurable in `/backend/config/benchmarks.yaml`:

```yaml
dart_benchmarks:
  "236220": 3.5  # Commercial building construction
  "238160": 5.0  # Roofing contractors  
  "238120": 4.2  # Structural steel contractors
```

## 🛡️ Compliance & Ethics

### Data Usage Guidelines
- Uses only **public regulatory data** (OSHA inspections, citations, ITA filings)
- **No private/confidential information** collection
- Respects robots.txt and rate limits for web scraping
- **Empathetic messaging** - never sensationalizes incidents

### Privacy & Security
- No personal information stored
- Company data limited to public records
- Rate limiting on external API calls
- Local development environment only

### Outreach Ethics
- **Empathy-first** approach to incident-related outreach
- Focus on **prevention and improvement**, not blame
- Professional, consultative tone
- Verify information against official sources

## 📋 Sample Data

The application includes realistic sample data:

- **8 subcontractors** with varying risk profiles
- **6 general contractors** across multiple states  
- **4 owners/developers** with active projects
- **30+ incidents** spanning inspections, accidents, citations
- **10 target opportunities** with generated outreach kits

### CSV Upload Formats

**Sub Relationships** (`samples/sub_relationships.csv`):
```csv
gc_name,owner_name,sub_name,project_name,location,start_date,end_date,trade,po_value
```

**Company Aliases** (`samples/company_aliases.csv`):
```csv
canonical_name,alias
```

## 🐛 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Change ports in docker-compose.yml if 3000/8000/5432 are in use
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # API
```

**Database connection issues:**
```bash
# Reset database
make clean
make demo
```

**Frontend build errors:**
```bash
# Clear node modules and rebuild
docker-compose exec web rm -rf node_modules
docker-compose exec web npm install
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with appropriate tests
4. Commit with descriptive messages
5. Push and create Pull Request

### Code Standards
- Python: Black formatting, type hints, docstrings
- TypeScript: ESLint, Prettier, strict types
- Commits: Conventional commit format
- Tests: Maintain >80% coverage

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions, issues, or feature requests:

1. Check existing [GitHub Issues](https://github.com/your-org/risk-radar/issues)
2. Create new issue with detailed description
3. Include steps to reproduce for bugs
4. Provide use case context for feature requests

---

**⚠️ Important**: This application is designed for **defensive security purposes only**. It helps identify opportunities for improving construction safety through enhanced prequal processes. Use responsibly and in compliance with all applicable laws and regulations.