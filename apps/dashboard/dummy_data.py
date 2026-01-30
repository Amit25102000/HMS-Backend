"""
Dummy Data Service for Dashboard APIs
Provides realistic mock data for development and demo purposes
"""
import random
from datetime import datetime, timedelta


class DummyDataService:
    """Service to generate realistic dummy data for dashboards"""
    
    @staticmethod
    def get_admin_dashboard_data():
        """Generate dummy data for admin dashboard"""
        return {
            'patients': {
                'total': 1240,
                'today': 18,
            },
            'doctors': {
                'total': 42,
                'active': 38,
            },
            'appointments': {
                'today': 87,
                'pending': 23,
                'confirmed': 54,
            },
            'revenue': {
                'today': 152000.00,
                'month': 4250000.00,
                'pending': 385000.00,
            },
            'inventory': {
                'total_medicines': 324,
                'low_stock': 12,
            }
        }
    
    @staticmethod
    def get_doctor_dashboard_data():
        """Generate dummy data for doctor dashboard"""
        return {
            'appointments': {
                'today': 12,
                'confirmed': 9,
                'pending': 3,
                'month': 156,
            },
            'patients': {
                'assigned': 46,
            },
            'prescriptions': {
                'pending': 4,
            }
        }
    
    @staticmethod
    def get_staff_dashboard_data():
        """Generate dummy data for staff dashboard"""
        return {
            'patients': {
                'new_today': 18,
                'total_active': 1240,
            },
            'appointments': {
                'today_total': 87,
                'pending': 23,
                'confirmed': 54,
                'completed': 10,
            },
            'billing': {
                'unpaid_invoices': 34,
                'partial_invoices': 12,
                'pending_amount': 385000.00,
                'today_revenue': 152000.00,
            }
        }
    
    @staticmethod
    def get_appointment_list(limit=50):
        """Generate dummy appointment list with realistic data"""
        first_names = ['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali', 'Karan', 'Neha', 'Rahul', 'Pooja', 
                       'Arjun', 'Divya', 'Rohan', 'Kavya', 'Aditya', 'Meera']
        last_names = ['Kumar', 'Sharma', 'Patel', 'Singh', 'Gupta', 'Reddy', 'Verma', 'Joshi', 'Malhotra', 'Nair',
                      'Chopra', 'Kapoor', 'Mehta', 'Shah', 'Desai', 'Iyer']
        doctor_names = ['Dr. Anil Kumar', 'Dr. Priya Shah', 'Dr. Rajesh Verma', 'Dr. Sanjay Patel', 
                        'Dr. Kavita Singh', 'Dr. Rohit Sharma', 'Dr. Meera Reddy', 'Dr. Amit Gupta']
        reasons = ['Regular Checkup', 'Follow-up', 'Emergency Consultation', 'Diagnostic Review', 
                   'Vaccination', 'Lab Results Review', 'Chronic Pain Management', 'Preventive Care']
        statuses = ['PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED']
        time_slots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', 
                      '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00']
        
        appointments = []
        today = datetime.now().date()
        
        for i in range(1, limit + 1):
            # Generate dates: some past, some today, some future
            days_offset = random.randint(-7, 14)  # 7 days ago to 14 days ahead
            apt_date = today + timedelta(days=days_offset)
            
            # Status logic: past appointments are mostly COMPLETED, future are PENDING/CONFIRMED
            if days_offset < 0:
                status = random.choice(['COMPLETED', 'COMPLETED', 'COMPLETED', 'CANCELLED', 'NO_SHOW'])
            elif days_offset == 0:
                status = random.choice(['PENDING', 'CONFIRMED', 'CONFIRMED', 'COMPLETED'])
            else:
                status = random.choice(['PENDING', 'PENDING', 'CONFIRMED'])
            
            patient_first = random.choice(first_names)
            patient_last = random.choice(last_names)
            
            appointments.append({
                'id': i,
                'appointment_id': f'APT-{apt_date.strftime("%Y%m%d")}-{i:04d}',
                'patient': i,
                'patient_name': f'{patient_first} {patient_last}',
                'patient_phone': f'+91 {random.randint(7000000000, 9999999999)}',
                'doctor': random.randint(1, 8),
                'doctor_name': random.choice(doctor_names),
                'appointment_date': apt_date.isoformat(),
                'appointment_time': random.choice(time_slots),
                'status': status,
                'reason': random.choice(reasons),
                'notes': 'Patient consulted successfully' if status == 'COMPLETED' else '',
                'created_at': (apt_date - timedelta(days=random.randint(1, 3))).isoformat(),
            })
        
        # Sort by date (newest first)
        appointments.sort(key=lambda x: (x['appointment_date'], x['appointment_time']), reverse=True)
        return appointments
    
    @staticmethod
    def get_patient_list(limit=20):
        """Generate dummy patient list"""
        first_names = ['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali', 'Karan', 'Neha', 'Rahul', 'Pooja']
        last_names = ['Kumar', 'Sharma', 'Patel', 'Singh', 'Gupta', 'Reddy', 'Verma', 'Joshi', 'Malhotra', 'Nair']
        
        patients = []
        for i in range(1, limit + 1):
            patients.append({
                'id': i,
                'patient_id': f'PAT-{i:04d}',
                'first_name': random.choice(first_names),
                'last_name': random.choice(last_names),
                'age_years': random.randint(5, 85),
                'gender': random.choice(['M', 'F']),
                'phone': f'+91 {random.randint(7000000000, 9999999999)}',
                'is_active': True,
            })
        return patients
    
    @staticmethod
    def get_medicine_list(limit=20):
        """Generate dummy medicine inventory"""
        medicines = [
            'Paracetamol', 'Amoxicillin', 'Ciprofloxacin', 'Azithromycin',
            'Metformin', 'Amlodipine', 'Atorvastatin', 'Omeprazole',
            'Cetirizine', 'Ibuprofen', 'Aspirin', 'Insulin',
        ]
        
        inventory = []
        for i, med_name in enumerate(medicines[:limit], 1):
            inventory.append({
                'id': i,
                'name': med_name,
                'generic_name': f'Generic {med_name}',
                'stock_quantity': random.randint(50, 1000),
                'reorder_level': 100,
                'unit_price': round(random.uniform(10, 500), 2),
                'is_low_stock': random.random() < 0.2,
            })
        return inventory
    
    @staticmethod
    def get_report_list(limit=50):
        """Generate dummy report list with realistic data"""
        first_names = ['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anjali', 'Karan', 'Neha', 'Rahul', 'Pooja',
                       'Arjun', 'Divya', 'Rohan', 'Kavya', 'Aditya', 'Meera']
        last_names = ['Kumar', 'Sharma', 'Patel', 'Singh', 'Gupta', 'Reddy', 'Verma', 'Joshi', 'Malhotra', 'Nair',
                      'Chopra', 'Kapoor', 'Mehta', 'Shah', 'Desai', 'Iyer']
        doctor_names = ['Dr. Anil Kumar', 'Dr. Priya Shah', 'Dr. Rajesh Verma', 'Dr. Sanjay Patel',
                        'Dr. Kavita Singh', 'Dr. Rohit Sharma', 'Dr. Meera Reddy', 'Dr. Amit Gupta']
        report_types = [
            ('BLOOD_TEST', 'Blood Test'),
            ('XRAY', 'X-Ray'),
            ('MRI', 'MRI Scan'),
            ('CT_SCAN', 'CT Scan'),
            ('ULTRASOUND', 'Ultrasound'),
            ('ECG', 'ECG'),
            ('PATHOLOGY', 'Pathology'),
            ('RADIOLOGY', 'Radiology'),
        ]
        statuses = [
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('REVIEWED', 'Reviewed'),
        ]
        
        findings_templates = [
            'Normal results, no abnormalities detected',
            'Mild inflammation observed, recommend follow-up',
            'Test results within normal range',
            'Slight elevation in markers, monitoring advised',
            'All parameters normal',
            'Minor irregularities, further testing recommended',
        ]
        
        reports = []
        today = datetime.now().date()
        
        for i in range(1, limit + 1):
            # Generate dates: mostly recent
            days_offset = random.randint(-30, 0)  # Last 30 days
            report_date = today + timedelta(days=days_offset)
            
            # Status logic: older reports are more likely completed/reviewed
            if days_offset < -15:
                status_key, status_display = random.choice([statuses[1], statuses[2]])  # COMPLETED or REVIEWED
            elif days_offset < -7:
                status_key, status_display = random.choice([statuses[0], statuses[1]])  # PENDING or COMPLETED
            else:
                status_key, status_display = statuses[0]  # PENDING
            
            patient_first = random.choice(first_names)
            patient_last = random.choice(last_names)
            report_type_key, report_type_display = random.choice(report_types)
            
            reports.append({
                'id': i,
                'report_id': f'REP-{report_date.strftime("%Y%m%d")}-{i:04d}',
                'patient': i,
                'patient_name': f'{patient_first} {patient_last}',
                'patient_id': f'PAT-{i:04d}',
                'patient_phone': f'+91 {random.randint(7000000000, 9999999999)}',
                'doctor': random.randint(1, 8),
                'doctor_name': random.choice(doctor_names),
                'report_type': report_type_key,
                'report_type_display': report_type_display,
                'report_date': report_date.isoformat(),
                'status': status_key,
                'status_display': status_display,
                'findings': random.choice(findings_templates) if status_key != 'PENDING' else '',
                'file': None,
                'created_at': (report_date - timedelta(days=random.randint(0, 2))).isoformat(),
                'updated_at': report_date.isoformat(),
            })
        
        # Sort by date (newest first)
        reports.sort(key=lambda x: x['report_date'], reverse=True)
        return reports


# Singleton instance
dummy_service = DummyDataService()
