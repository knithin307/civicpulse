# CivicPulse — Smart City Issue Reporting & Resolution Platform
### Aligned with UN Sustainable Development Goal 11 (Sustainable Cities and Communities)

**CivicPulse** is an enterprise-grade full-stack civic technology web platform designed to streamline the reporting, triage, SLA tracking, resolution verification, and citizen auditing of urban infrastructure problems (potholes, garbage overflows, damaged streetlights, water pipeline bursts, and drainage hazards).

---

## 🌟 UN SDG 11 Alignment
- **Target 11.1 (Safe & Resilient Basic Services):** Rapid detection and repair of damaged roadway infrastructure, unlit street corridors, and potable water network bursts.
- **Target 11.6 (Urban Environmental Impact & Waste):** Prompt eradication of solid waste overflow spots, storm drain blockages, and stagnant vector breeding sites.
- **Participatory Urban Governance:** Real-time feedback loops between citizens, municipal field officers, and city administrators.

---

## 🛠️ Technology Stack
- **Backend**: Python 3.14, Flask (Application Factory pattern & modular Blueprints).
- **Database & ORM**: SQLite, Flask-SQLAlchemy (relational integrity, foreign keys, cascade rules).
- **Authentication & RBAC**: Flask-Login, Werkzeug password security (`generate_password_hash`, `check_password_hash`), granular role-based decorators (`citizen`, `officer`, `admin`).
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Jinja2 templating with reusable macros.
- **Geospatial & Mapping**: Leaflet.js with OpenStreetMap tiles (coordinate picker, interactive explorer map, marker clustering, popups).
- **Analytics & Data Visualizations**: Chart.js (Doughnut category distribution, Line 6-month resolution velocity, Bar pipeline status, Pie severity mix).
- **Automated Testing**: `pytest` covering authentication, authorization boundaries (RBAC), issue lifecycle service, and REST APIs.

---

## 🏗️ Project Architecture & Directory Structure
```
d:\CivicPulse\
├── app/
│   ├── __init__.py               # Flask application factory, filters, context processors
│   ├── config.py                 # Development, Testing, and Production configurations
│   ├── extensions.py             # SQLAlchemy and LoginManager instances
│   ├── models/                   # Relational domain models
│   │   ├── __init__.py           # Model exports
│   │   ├── user.py               # User model & UserRole constants
│   │   ├── department.py         # Municipal Department model
│   │   ├── category.py           # Problem Category & SLA definitions
│   │   ├── issue.py              # Issue, IssueTimeline, IssueUpvote models
│   │   └── feedback.py           # Citizen satisfaction feedback & ratings
│   ├── blueprints/               # Modular route controllers
│   │   ├── auth/                 # Sign In, Registration, Profile, Logout
│   │   ├── main/                 # Home, Interactive Map, Track by ID, SDG 11
│   │   ├── citizen/              # Citizen Dashboard, Report Issue, Issue Detail, Feedback
│   │   ├── officer/              # Department Queue, Status Updates, Resolution Evidence
│   │   ├── admin/                # Executive Command Center, Triage, Users, Analytics
│   │   └── api/                  # GeoJSON endpoints, AJAX upvotes, Chart.js stats
│   ├── services/                 # Business logic layer
│   │   ├── issue_service.py      # Issue lifecycle, SLA calculation, timeline audit
│   │   └── analytics_service.py  # Real database aggregations & KPI computation
│   ├── utils/                    # Decorators, secure file upload handlers, helpers
│   │   ├── decorators.py         # @role_required, @citizen_required, @officer_required
│   │   ├── file_upload.py        # Safe photo upload with UUID prefixing
│   │   └── helpers.py            # Naive UTC datetime helper for SQLite
│   ├── static/                   # Static assets
│   │   ├── css/civicpulse.css    # Premium deep navy, teal, white, green theme
│   │   ├── js/main.js            # Global alerts & AJAX upvoting
│   │   ├── js/map_picker.js      # Leaflet location pin dragger & geolocation
│   │   ├── js/explore_map.js     # GeoJSON map with status-colored markers & popups
│   │   ├── js/charts.js          # Dynamic Chart.js dashboard integration
│   │   └── uploads/              # Before and after photo storage
│   └── templates/                # Jinja2 HTML templates
│       ├── base.html             # Base layout with CDNs and navigation
│       ├── components/           # Navbar, Footer, Status badge macros
│       ├── errors/               # 403, 404, 500 error views
│       ├── auth/                 # Login, Register, Profile views
│       ├── main/                 # Index, Explore Map, Track, SDG 11 views
│       ├── citizen/              # Dashboard, My Reports, Report Form, Detail
│       ├── officer/              # Dispatch Queue, Resolution Proof Form
│       └── admin/                # Dashboard, Issues Registry, Departments, Users, Analytics
├── instance/
│   └── civicpulse.db             # Persistent SQLite database
├── tests/                        # Comprehensive test suite (19 test cases)
│   ├── conftest.py               # Fixtures, client, memory DB setup
│   ├── test_auth.py              # Registration, login, password check, profile
│   ├── test_rbac.py              # Role permissions boundary enforcement
│   ├── test_issues.py            # Issue creation, timeline, resolution, upvotes
│   └── test_api.py               # GeoJSON, analytics stats, categories
├── run.py                        # Local execution entry point
├── seed_data.py                  # Realistic smart city database seeder
├── requirements.txt              # Python dependencies
└── README.md                     # Documentation
```

---

## 🚀 Quickstart & Setup (Windows)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Seed the Database
Populate municipal departments, categories, realistic civic issues with before/after photo evidence, and demo accounts:
```powershell
python seed_data.py
```

### 3. Run the Application
```powershell
python run.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Demo Accounts (Pre-configured for Testing)

| Role | Email Address | Password | Scope & Department |
|---|---|---|---|
| **City Administrator** | `admin@civicpulse.org` | `admin123` | System-wide command center, issue routing, departments, users, CSV export |
| **Roads Officer** | `officer.roads@civicpulse.org` | `officer123` | Roads & Infrastructure department queue, pothole triage, resolution proof |
| **Waste Management Officer** | `officer.waste@civicpulse.org` | `officer123` | Solid Waste Management queue, sanitation triage |
| **Water Supply Officer** | `officer.water@civicpulse.org` | `officer123` | Water & Sewerage queue, pipeline rupture dispatch |
| **Electrical Officer** | `officer.power@civicpulse.org` | `officer123` | Electrical & Public Lighting queue, streetlight repairs |
| **Citizen** | `citizen@civicpulse.org` | `citizen123` | Report hazards with map picker, track issues, submit ratings & feedback |

> **Pro Tip**: The Sign In page includes **1-Click Quick Demo Role Fillers** to instantly populate credentials for Admin, Officer, or Citizen with a single click.

---

## 🧪 Running Automated Tests
Run the complete `pytest` test suite:
```powershell
python -m pytest tests/ -v
```
All **19 tests** execute in under 3 seconds with in-memory SQLite isolation.

---

## 📊 Key Highlights & Verification
1. **Persistent SQLite Database**: Real database queries, aggregations, and cascading foreign keys.
2. **Zero Hardcoded Statistics**: All KPI cards, resolution rates, SLA adherence percentages, and Chart.js visuals are dynamically computed from live SQL queries.
3. **Resolution Evidence Verification**: Field officers must upload after-repair photographic proof and detailed work notes, which are displayed side-by-side with original photos on the citizen's audit card.
4. **Interactive Leaflet Mapping**: Draggable GPS pin picker, geolocation detection, and GeoJSON map explorer.
5. **Role-Based Security**: Complete backend authorization boundaries prevent unauthorized role access.
