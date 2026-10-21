import os
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.category import Category
from app.models.issue import Issue, IssueTimeline, IssueStatus, IssuePriority, IssueUpvote
from app.models.feedback import Feedback
from app.utils.helpers import get_utc_now

def create_sample_svg(filepath, text, bg_color="#0b192c", text_color="#ffffff"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <rect width="100%" height="100%" fill="{bg_color}"/>
  <rect x="20" y="20" width="560" height="360" rx="15" fill="none" stroke="{text_color}" stroke-opacity="0.3" stroke-width="2" stroke-dasharray="8 8"/>
  <circle cx="300" cy="180" r="45" fill="{text_color}" fill-opacity="0.1"/>
  <path d="M300 150 L320 200 L280 200 Z" fill="{text_color}" fill-opacity="0.8"/>
  <text x="50%" y="260" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="bold" fill="{text_color}" text-anchor="middle">{text}</text>
  <text x="50%" y="295" font-family="system-ui, -apple-system, sans-serif" font-size="14" fill="{text_color}" fill-opacity="0.7" text-anchor="middle">CivicPulse Smart City Municipal Verification Evidence</text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)

def seed_database():
    app = create_app('development')
    with app.app_context():
        # Clean slate or inspect existing
        db.create_all()
        
        # Check if already seeded
        if User.query.filter_by(email='admin@civicpulse.org').first():
            print("Database already contains seed data. Skipping re-seed.")
            return

        print("Seeding CivicPulse database with realistic smart city data...")
        
        # Setup sample images
        issues_dir = os.path.join(app.root_path, 'static', 'uploads', 'issues')
        res_dir = os.path.join(app.root_path, 'static', 'uploads', 'resolutions')
        os.makedirs(issues_dir, exist_ok=True)
        os.makedirs(res_dir, exist_ok=True)
        
        create_sample_svg(os.path.join(issues_dir, 'pothole_before.svg'), 'Reported: Severe Road Crater Pothole', bg_color='#2c1810', text_color='#ff7675')
        create_sample_svg(os.path.join(res_dir, 'pothole_after.svg'), 'Resolved: Fresh Bitumen Overlay Applied', bg_color='#0f2d1e', text_color='#55efc4')
        
        create_sample_svg(os.path.join(issues_dir, 'garbage_before.svg'), 'Reported: Waste Bin Overflow & Stagnation', bg_color='#2d1f05', text_color='#fdcb6e')
        create_sample_svg(os.path.join(res_dir, 'garbage_after.svg'), 'Resolved: Cleared & Disinfected Dump Site', bg_color='#0f2d1e', text_color='#55efc4')
        
        create_sample_svg(os.path.join(issues_dir, 'streetlight_before.svg'), 'Reported: Damaged Pole & Dark Crossing', bg_color='#111b2b', text_color='#74b9ff')
        create_sample_svg(os.path.join(res_dir, 'streetlight_after.svg'), 'Resolved: 80W LED Fitting Restored', bg_color='#0f2d1e', text_color='#55efc4')

        create_sample_svg(os.path.join(issues_dir, 'water_leak_before.svg'), 'Reported: 4-inch Sub-main Water Pipe Rupture', bg_color='#092327', text_color='#00cec9')
        create_sample_svg(os.path.join(res_dir, 'water_leak_after.svg'), 'Resolved: Pipeline Replaced & Road Sealed', bg_color='#0f2d1e', text_color='#55efc4')

        # 1. Departments
        depts_data = [
            {
                'name': 'Roads & Infrastructure',
                'code': 'ROADS',
                'description': 'Municipal roadway maintenance, asphalt resurfacing, pavement repair, and bridge structures.',
                'contact_email': 'roads.dept@civicpulse.org',
                'contact_phone': '+1 (555) 019-4821',
                'icon': 'bi-cone-striped'
            },
            {
                'name': 'Solid Waste Management',
                'code': 'WASTE',
                'description': 'Daily municipal solid waste collection, recycling coordination, and illegal dumpsite eradication.',
                'contact_email': 'waste.dept@civicpulse.org',
                'contact_phone': '+1 (555) 019-4822',
                'icon': 'bi-trash3'
            },
            {
                'name': 'Electrical & Public Lighting',
                'code': 'POWER',
                'description': 'Smart street lighting network, transformer maintenance, and hazardous cable insulation.',
                'contact_email': 'power.dept@civicpulse.org',
                'contact_phone': '+1 (555) 019-4823',
                'icon': 'bi-lightbulb'
            },
            {
                'name': 'Water Supply & Sewerage',
                'code': 'WATER',
                'description': 'Potable water pipelines, stormwater drainage network, sewer mains, and flood management.',
                'contact_email': 'water.dept@civicpulse.org',
                'contact_phone': '+1 (555) 019-4824',
                'icon': 'bi-droplet-half'
            },
            {
                'name': 'Environment & Public Health',
                'code': 'HEALTH',
                'description': 'Urban sanitation inspections, stagnant water fogging, noise control, and public park upkeep.',
                'contact_email': 'health.dept@civicpulse.org',
                'contact_phone': '+1 (555) 019-4825',
                'icon': 'bi-tree'
            }
        ]
        
        departments = {}
        for d in depts_data:
            dept = Department(**d)
            db.session.add(dept)
            departments[d['code']] = dept
            
        db.session.flush()

        # 2. Categories
        categories_data = [
            {
                'name': 'Potholes & Broken Asphalt',
                'department_id': departments['ROADS'].id,
                'description': 'Dangerous craters, sunken manhole lids, and surface cracks on public roads.',
                'icon': 'bi-cone-striped',
                'default_severity': IssuePriority.HIGH,
                'sla_hours': 24
            },
            {
                'name': 'Sidewalk & Pavement Damage',
                'department_id': departments['ROADS'].id,
                'description': 'Broken pedestrian walkways, missing curb stones, and pedestrian obstacles.',
                'icon': 'bi-signpost-split',
                'default_severity': IssuePriority.MEDIUM,
                'sla_hours': 48
            },
            {
                'name': 'Overflowing Garbage Bins',
                'department_id': departments['WASTE'].id,
                'description': 'Public garbage containers exceeding capacity with litter on roadsides.',
                'icon': 'bi-trash',
                'default_severity': IssuePriority.HIGH,
                'sla_hours': 12
            },
            {
                'name': 'Illegal Waste Dumping',
                'department_id': departments['WASTE'].id,
                'description': 'Debris, construction rubble, or commercial waste deposited in unauthorized public areas.',
                'icon': 'bi-exclamation-octagon',
                'default_severity': IssuePriority.HIGH,
                'sla_hours': 24
            },
            {
                'name': 'Broken Streetlights / Dark Spots',
                'department_id': departments['POWER'].id,
                'description': 'Unlit poles, flickering bulbs, and dark pedestrian corridors compromising nocturnal safety.',
                'icon': 'bi-lightbulb-off',
                'default_severity': IssuePriority.MEDIUM,
                'sla_hours': 24
            },
            {
                'name': 'Exposed Electrical Cables',
                'department_id': departments['POWER'].id,
                'description': 'Hanging live wires, damaged junction boxes, or spark hazards.',
                'icon': 'bi-lightning-charge',
                'default_severity': IssuePriority.CRITICAL,
                'sla_hours': 6
            },
            {
                'name': 'Water Pipeline Burst & Leakage',
                'department_id': departments['WATER'].id,
                'description': 'High-pressure clean water leaks, bubbling asphalt, or pressure drop.',
                'icon': 'bi-water',
                'default_severity': IssuePriority.CRITICAL,
                'sla_hours': 12
            },
            {
                'name': 'Clogged Stormwater Drains',
                'department_id': departments['WATER'].id,
                'description': 'Gutter blockages causing waterlogging during rain spells.',
                'icon': 'bi-tsunami',
                'default_severity': IssuePriority.HIGH,
                'sla_hours': 24
            },
            {
                'name': 'Stagnant Water & Vector Menace',
                'department_id': departments['HEALTH'].id,
                'description': 'Standing water reservoirs breeding mosquitoes and foul odor.',
                'icon': 'bi-bug',
                'default_severity': IssuePriority.MEDIUM,
                'sla_hours': 48
            }
        ]
        
        categories = {}
        for c in categories_data:
            cat = Category(**c)
            db.session.add(cat)
            categories[c['name']] = cat
            
        db.session.flush()

        # 3. Users
        # Admin
        admin = User(
            full_name='City Administrator Elena Vance',
            email='admin@civicpulse.org',
            phone='+1 (555) 789-0001',
            role=UserRole.ADMIN
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Officers
        officer_roads = User(
            full_name='Eng. Marcus Sterling',
            email='officer.roads@civicpulse.org',
            phone='+1 (555) 789-0010',
            role=UserRole.OFFICER,
            department_id=departments['ROADS'].id
        )
        officer_roads.set_password('officer123')
        db.session.add(officer_roads)

        officer_waste = User(
            full_name='Insp. Sarah Jenkins',
            email='officer.waste@civicpulse.org',
            phone='+1 (555) 789-0020',
            role=UserRole.OFFICER,
            department_id=departments['WASTE'].id
        )
        officer_waste.set_password('officer123')
        db.session.add(officer_waste)

        officer_water = User(
            full_name='Eng. David Morales',
            email='officer.water@civicpulse.org',
            phone='+1 (555) 789-0030',
            role=UserRole.OFFICER,
            department_id=departments['WATER'].id
        )
        officer_water.set_password('officer123')
        db.session.add(officer_water)

        officer_power = User(
            full_name='Tech. Priya Patel',
            email='officer.power@civicpulse.org',
            phone='+1 (555) 789-0040',
            role=UserRole.OFFICER,
            department_id=departments['POWER'].id
        )
        officer_power.set_password('officer123')
        db.session.add(officer_power)

        officer_health = User(
            full_name='Dr. Carlos Rivera',
            email='officer.health@civicpulse.org',
            phone='+1 (555) 789-0050',
            role=UserRole.OFFICER,
            department_id=departments['HEALTH'].id
        )
        officer_health.set_password('officer123')
        db.session.add(officer_health)

        # Citizens
        citizen1 = User(
            full_name='Alex Johnson',
            email='citizen@civicpulse.org',
            phone='+1 (555) 432-1100',
            role=UserRole.CITIZEN
        )
        citizen1.set_password('citizen123')
        db.session.add(citizen1)

        citizen2 = User(
            full_name='Maya Lin',
            email='citizen.jane@civicpulse.org',
            phone='+1 (555) 432-1200',
            role=UserRole.CITIZEN
        )
        citizen2.set_password('citizen123')
        db.session.add(citizen2)

        db.session.flush()

        # 4. Realistic Smart City Civic Issues (spread over city coordinates: ~12.9716, 77.5946)
        now = get_utc_now()
        
        # Issue 1: Resolved Pothole
        created_1 = now - timedelta(days=5, hours=4)
        resolved_1 = created_1 + timedelta(hours=18) # Under 24h SLA
        issue_1 = Issue(
            tracking_id='CP-2026-1042',
            title='Severe 2ft Pothole opposite Central Metro Station Gate 3',
            description='Vehicles are violently swerving to avoid this deep pothole near the pedestrian crossing. Multiple two-wheeler skids observed during morning peak hours.',
            category_id=categories['Potholes & Broken Asphalt'].id,
            department_id=departments['ROADS'].id,
            citizen_id=citizen1.id,
            status=IssueStatus.RESOLVED,
            priority=IssuePriority.HIGH,
            address='MG Road, Opposite Metro Gate 3, Central Ward',
            latitude=12.9752,
            longitude=77.5998,
            image_before='uploads/issues/pothole_before.svg',
            image_after='uploads/resolutions/pothole_after.svg',
            resolution_notes='Municipal rapid road maintenance team deployed. Excavated loose base course, backfilled with hot-mix bituminous concrete, compacted with 8-ton vibratory roller, and marked with reflective thermal striping.',
            resolved_by_officer_id=officer_roads.id,
            created_at=created_1,
            updated_at=resolved_1,
            resolved_at=resolved_1,
            upvotes_count=18,
            is_public=True
        )
        db.session.add(issue_1)
        db.session.flush()
        
        db.session.add(IssueTimeline(
            issue_id=issue_1.id, user_id=citizen1.id, action='Issue Reported',
            old_status=None, new_status=IssueStatus.SUBMITTED,
            remarks='Initial report submitted with geo-coordinates and hazard photo.',
            created_at=created_1
        ))
        db.session.add(IssueTimeline(
            issue_id=issue_1.id, user_id=admin.id, action='Assigned to Roads & Infrastructure',
            old_status=IssueStatus.SUBMITTED, new_status=IssueStatus.UNDER_REVIEW,
            remarks='Auto-routed and confirmed by Central Admin.',
            created_at=created_1 + timedelta(minutes=40)
        ))
        db.session.add(IssueTimeline(
            issue_id=issue_1.id, user_id=officer_roads.id, action='Crew Dispatched',
            old_status=IssueStatus.UNDER_REVIEW, new_status=IssueStatus.IN_PROGRESS,
            remarks='Work order #RD-8841 issued to Rapid Asphalt Repair Squad 2.',
            created_at=created_1 + timedelta(hours=3)
        ))
        db.session.add(IssueTimeline(
            issue_id=issue_1.id, user_id=officer_roads.id, action='Resolution Completed & Evidence Submitted',
            old_status=IssueStatus.IN_PROGRESS, new_status=IssueStatus.RESOLVED,
            remarks='Patching and rolling complete. Surface test passed.',
            created_at=resolved_1
        ))
        
        # Feedback for Issue 1
        db.session.add(Feedback(
            issue_id=issue_1.id,
            citizen_id=citizen1.id,
            rating=5,
            satisfaction='satisfied',
            comments='Incredible turnaround time! Fixed cleanly within 18 hours. Great initiative for city safety.',
            created_at=resolved_1 + timedelta(hours=2)
        ))

        # Issue 2: Resolved Waste Overflow
        created_2 = now - timedelta(days=3, hours=8)
        resolved_2 = created_2 + timedelta(hours=8) # Within 12h SLA
        issue_2 = Issue(
            tracking_id='CP-2026-2108',
            title='Commercial Garbage Overflow near Green Valley Market',
            description='Market waste bins have been overflowing onto the pavement for 2 days. Stray dogs scattering litter across storm drains.',
            category_id=categories['Overflowing Garbage Bins'].id,
            department_id=departments['WASTE'].id,
            citizen_id=citizen2.id,
            status=IssueStatus.RESOLVED,
            priority=IssuePriority.HIGH,
            address='14th Main, 4th Sector, Market Square',
            latitude=12.9680,
            longitude=77.5890,
            image_before='uploads/issues/garbage_before.svg',
            image_after='uploads/resolutions/garbage_after.svg',
            resolution_notes='Mechanical compactor truck dispatched. All perimeter waste collected, bins washed, and area sprayed with bio-sanitizing solution.',
            resolved_by_officer_id=officer_waste.id,
            created_at=created_2,
            updated_at=resolved_2,
            resolved_at=resolved_2,
            upvotes_count=12,
            is_public=True
        )
        db.session.add(issue_2)
        db.session.flush()
        
        db.session.add(IssueTimeline(
            issue_id=issue_2.id, user_id=citizen2.id, action='Issue Reported',
            old_status=None, new_status=IssueStatus.SUBMITTED,
            remarks='Citizen reported sanitation problem.',
            created_at=created_2
        ))
        db.session.add(IssueTimeline(
            issue_id=issue_2.id, user_id=officer_waste.id, action='Resolution Completed & Evidence Submitted',
            old_status=IssueStatus.IN_PROGRESS, new_status=IssueStatus.RESOLVED,
            remarks='Full site sanitation and compaction sweep executed.',
            created_at=resolved_2
        ))
        db.session.add(Feedback(
            issue_id=issue_2.id,
            citizen_id=citizen2.id,
            rating=5,
            satisfaction='satisfied',
            comments='Cleaned thoroughly before morning market opened. Very impressed.',
            created_at=resolved_2 + timedelta(hours=1)
        ))

        # Issue 3: In Progress Water Pipeline Burst
        created_3 = now - timedelta(hours=10)
        issue_3 = Issue(
            tracking_id='CP-2026-3490',
            title='High-Pressure Potable Water Main Rupture on Park Boulevard',
            description='Sub-surface drinking water line ruptured. Water gushing across two lanes of roadway, causing severe pressure drop in neighboring residential blocks.',
            category_id=categories['Water Pipeline Burst & Leakage'].id,
            department_id=departments['WATER'].id,
            citizen_id=citizen1.id,
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.CRITICAL,
            address='Park Boulevard & 8th Cross Junction',
            latitude=12.9815,
            longitude=77.6052,
            image_before='uploads/issues/water_leak_before.svg',
            image_after=None,
            resolution_notes=None,
            resolved_by_officer_id=None,
            created_at=created_3,
            updated_at=now - timedelta(hours=3),
            upvotes_count=29,
            is_public=True
        )
        db.session.add(issue_3)
        db.session.flush()
        
        db.session.add(IssueTimeline(
            issue_id=issue_3.id, user_id=citizen1.id, action='Issue Reported',
            old_status=None, new_status=IssueStatus.SUBMITTED,
            remarks='Emergency civic report logged.',
            created_at=created_3
        ))
        db.session.add(IssueTimeline(
            issue_id=issue_3.id, user_id=officer_water.id, action='Emergency Isolation Valve Shut',
            old_status=IssueStatus.SUBMITTED, new_status=IssueStatus.IN_PROGRESS,
            remarks='Sector valve isolated to prevent further loss. Excavation backhoe onsite replacing 4-inch ductile iron collar.',
            created_at=created_3 + timedelta(hours=2)
        ))

        # Issue 4: Under Review Broken Streetlights
        created_4 = now - timedelta(hours=16)
        issue_4 = Issue(
            tracking_id='CP-2026-4512',
            title='4 Consecutive Streetlights Non-Operational along Lake Promenade',
            description='Pedestrian walkway is in total darkness. Women and joggers feeling unsafe in the evening. Underground breaker appears tripped.',
            category_id=categories['Broken Streetlights / Dark Spots'].id,
            department_id=departments['POWER'].id,
            citizen_id=citizen2.id,
            status=IssueStatus.UNDER_REVIEW,
            priority=IssuePriority.MEDIUM,
            address='Lake Promenade Walkway, South Basin',
            latitude=12.9550,
            longitude=77.5820,
            image_before='uploads/issues/streetlight_before.svg',
            created_at=created_4,
            updated_at=now - timedelta(hours=5),
            upvotes_count=8,
            is_public=True
        )
        db.session.add(issue_4)
        db.session.flush()
        
        db.session.add(IssueTimeline(
            issue_id=issue_4.id, user_id=citizen2.id, action='Issue Reported',
            old_status=None, new_status=IssueStatus.SUBMITTED,
            remarks='Report logged.',
            created_at=created_4
        ))
        db.session.add(IssueTimeline(
            issue_id=issue_4.id, user_id=officer_power.id, action='Inspection Assigned',
            old_status=IssueStatus.SUBMITTED, new_status=IssueStatus.UNDER_REVIEW,
            remarks='Night patrol electrical inspector scheduled to test feeder pillar.',
            created_at=created_4 + timedelta(hours=4)
        ))

        # Issue 5: Submitted Clogged Stormwater Drain
        created_5 = now - timedelta(hours=4)
        issue_5 = Issue(
            tracking_id='CP-2026-5821',
            title='Silt and Plastic Bottle Clog in Main Storm Drain Grate',
            description='Stormwater inlet completely blocked by accumulated single-use plastics and construction dirt. First rainfall will cause instant localized flooding.',
            category_id=categories['Clogged Stormwater Drains'].id,
            department_id=departments['WATER'].id,
            citizen_id=citizen1.id,
            status=IssueStatus.SUBMITTED,
            priority=IssuePriority.HIGH,
            address='Outer Ring Road, Underpass Ramp B',
            latitude=12.9890,
            longitude=77.6180,
            image_before=None,
            created_at=created_5,
            updated_at=created_5,
            upvotes_count=14,
            is_public=True
        )
        db.session.add(issue_5)
        db.session.flush()
        
        db.session.add(IssueTimeline(
            issue_id=issue_5.id, user_id=citizen1.id, action='Issue Reported',
            old_status=None, new_status=IssueStatus.SUBMITTED,
            remarks='Citizen submitted issue report with coordinates.',
            created_at=created_5
        ))

        # Issue 6: Resolved Streetlight repair
        created_6 = now - timedelta(days=2, hours=14)
        resolved_6 = created_6 + timedelta(hours=14)
        issue_6 = Issue(
            tracking_id='CP-2026-6192',
            title='Flickering High-Mast Light at Hospital Cross Junction',
            description='High mast fitting stroboscopic flicker causing driver disorientation at night.',
            category_id=categories['Broken Streetlights / Dark Spots'].id,
            department_id=departments['POWER'].id,
            citizen_id=citizen2.id,
            status=IssueStatus.RESOLVED,
            priority=IssuePriority.MEDIUM,
            address='Hospital Cross & University Ave',
            latitude=12.9640,
            longitude=77.6100,
            image_before='uploads/issues/streetlight_before.svg',
            image_after='uploads/resolutions/streetlight_after.svg',
            resolution_notes='Defective LED driver module replaced. Tested illumination output at 110 lux across intersection.',
            resolved_by_officer_id=officer_power.id,
            created_at=created_6,
            updated_at=resolved_6,
            resolved_at=resolved_6,
            upvotes_count=7,
            is_public=True
        )
        db.session.add(issue_6)
        db.session.flush()
        
        db.session.add(Feedback(
            issue_id=issue_6.id,
            citizen_id=citizen2.id,
            rating=4,
            satisfaction='satisfied',
            comments='Fixed properly, thanks to the electrical team.',
            created_at=resolved_6 + timedelta(hours=3)
        ))

        # Upvote relations
        db.session.add(IssueUpvote(issue_id=issue_1.id, user_id=citizen1.id))
        db.session.add(IssueUpvote(issue_id=issue_1.id, user_id=citizen2.id))
        db.session.add(IssueUpvote(issue_id=issue_3.id, user_id=citizen1.id))
        db.session.add(IssueUpvote(issue_id=issue_3.id, user_id=citizen2.id))

        db.session.commit()
        print("CivicPulse database seeded successfully!")
        print("\n=== Demo Accounts ===")
        print("Admin:   admin@civicpulse.org   / admin123")
        print("Officer: officer.roads@civicpulse.org / officer123")
        print("Officer: officer.waste@civicpulse.org / officer123")
        print("Officer: officer.water@civicpulse.org / officer123")
        print("Officer: officer.power@civicpulse.org / officer123")
        print("Citizen: citizen@civicpulse.org / citizen123")
        print("=====================\n")

if __name__ == '__main__':
    seed_database()
