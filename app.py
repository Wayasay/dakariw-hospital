from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import random
import uuid

app = Flask(__name__)

# Order Storage (in-memory - will reset on server restart)
ORDERS = []

# Order status: pending -> accepted -> in_progress -> completed
ORDER_STATUS = {
    'pending': 'Pending',
    'accepted': 'Accepted',
    'in_progress': 'In Progress',
    'completed': 'Completed'
}

# Patient Database
PATIENTS = {
    "P001": {
        "id": "P001",
        "name": "Sarah Chen",
        "age": 58,
        "dob": "1968-03-15",
        "condition": "Type 2 Diabetes",
        "dietary_needs": ["Low glycemic index", "Controlled carbohydrates", "High fiber"],
        "restrictions": ["Refined sugars", "White bread", "Sugary drinks"],
        "avatar_color": "#FF6B9D"
    },
    "P002": {
        "id": "P002",
        "name": "James Okoye",
        "age": 42,
        "dob": "1984-07-22",
        "condition": "Anemia (Low Iron)",
        "dietary_needs": ["Iron-rich foods", "Vitamin C", "Folate"],
        "restrictions": ["Tea with meals", "Excessive calcium"],
        "avatar_color": "#4ECDC4"
    },
    "P003": {
        "id": "P003",
        "name": "Maria Santos",
        "age": 65,
        "dob": "1961-11-08",
        "condition": "Hypertension",
        "dietary_needs": ["Low sodium", "Potassium-rich", "Heart-healthy fats"],
        "restrictions": ["Salt", "Processed foods", "High sodium condiments"],
        "avatar_color": "#95E1D3"
    },
    "P004": {
        "id": "P004",
        "name": "Ahmed Hassan",
        "age": 35,
        "dob": "1991-05-30",
        "condition": "Post-Surgery Recovery",
        "dietary_needs": ["High protein", "Vitamin C", "Zinc", "Calories for healing"],
        "restrictions": ["Spicy foods", "Hard-to-digest foods"],
        "avatar_color": "#FFE66D"
    },
    "P005": {
        "id": "P005",
        "name": "Linda Brown",
        "age": 71,
        "dob": "1955-09-12",
        "condition": "Chronic Kidney Disease (Stage 3)",
        "dietary_needs": ["Controlled protein", "Low potassium", "Low phosphorus"],
        "restrictions": ["High potassium foods", "Dairy products", "Dark leafy greens"],
        "avatar_color": "#A8E6CF"
    }
}

# Comprehensive Meal Database
MEALS = {
    # BREAKFAST OPTIONS
    "oatmeal_berries": {
        "name": "Steel-Cut Oatmeal with Berries",
        "type": "breakfast",
        "suitable_for": ["diabetes", "heart_health", "anemia"],
        "nutritional_info": {
            "calories": 320,
            "protein": "8g",
            "carbs": "52g",
            "fiber": "8g",
            "iron": "3.2mg"
        },
        "health_benefits": "Steel-cut oats have a low glycemic index (GI of 55), releasing glucose slowly into the bloodstream. Berries provide powerful antioxidants and additional soluble fiber that slows sugar absorption.",
        "why_needed": "For diabetic patients, this prevents dangerous blood sugar spikes after meals. The high fiber content (8g) improves insulin sensitivity and helps maintain stable glucose levels for 3-4 hours. The iron content also supports oxygen transport in the blood."
    },
    "spinach_omelette": {
        "name": "Spinach & Mushroom Omelette",
        "type": "breakfast",
        "suitable_for": ["anemia", "recovery", "kidney_disease"],
        "nutritional_info": {
            "calories": 280,
            "protein": "22g",
            "iron": "4.5mg",
            "vitamin_c": "15mg",
            "phosphorus": "Low"
        },
        "health_benefits": "Eggs provide complete protein with all essential amino acids. Spinach delivers non-heme iron, while vitamin C from tomatoes enhances iron absorption by up to 300%. Mushrooms add B-vitamins for energy metabolism.",
        "why_needed": "Critical for anemia patients - the combination of iron and vitamin C maximizes hemoglobin production. For recovery patients, the 22g of high-quality protein supports tissue repair and wound healing. Low in potassium for kidney patients."
    },
    "whole_grain_toast_avocado": {
        "name": "Whole Grain Toast with Avocado",
        "type": "breakfast",
        "suitable_for": ["heart_health", "diabetes"],
        "nutritional_info": {
            "calories": 340,
            "protein": "10g",
            "fiber": "12g",
            "potassium": "485mg",
            "healthy_fats": "15g"
        },
        "health_benefits": "Avocados contain monounsaturated fats that lower LDL (bad) cholesterol while raising HDL (good) cholesterol. Whole grains provide sustained energy without spiking blood sugar.",
        "why_needed": "For hypertension patients, the potassium (485mg) helps counteract sodium and relaxes blood vessel walls, reducing blood pressure. The healthy fats support cardiovascular health and reduce inflammation."
    },
    "greek_yogurt_nuts": {
        "name": "Greek Yogurt with Almonds & Honey",
        "type": "breakfast",
        "suitable_for": ["recovery", "diabetes"],
        "nutritional_info": {
            "calories": 350,
            "protein": "20g",
            "calcium": "250mg",
            "zinc": "2mg"
        },
        "health_benefits": "Greek yogurt provides probiotics for gut health and double the protein of regular yogurt. Almonds offer vitamin E for immune function and healthy fats. Natural honey provides quick energy.",
        "why_needed": "Post-surgery patients need high protein (20g) for collagen synthesis and wound closure. Zinc accelerates healing by supporting immune function and cell division. Probiotics prevent antibiotic-related digestive issues."
    },

    # LUNCH OPTIONS
    "grilled_salmon_quinoa": {
        "name": "Grilled Salmon with Quinoa & Steamed Broccoli",
        "type": "lunch",
        "suitable_for": ["heart_health", "diabetes", "recovery"],
        "nutritional_info": {
            "calories": 520,
            "protein": "38g",
            "omega3": "2.5g",
            "fiber": "8g",
            "sodium": "180mg"
        },
        "health_benefits": "Salmon provides omega-3 fatty acids (EPA and DHA) that reduce arterial inflammation and prevent plaque buildup. Quinoa is a complete protein with all 9 essential amino acids. Broccoli delivers vitamin K for blood clotting.",
        "why_needed": "For hypertension, omega-3s lower blood pressure by improving blood vessel elasticity. The low sodium (180mg) prevents fluid retention. Diabetics benefit from the protein and fiber combination that stabilizes blood sugar. Recovery patients get high-quality protein for tissue regeneration."
    },
    "chicken_breast_sweet_potato": {
        "name": "Herb-Roasted Chicken Breast with Sweet Potato",
        "type": "lunch",
        "suitable_for": ["recovery", "anemia", "diabetes"],
        "nutritional_info": {
            "calories": 480,
            "protein": "42g",
            "vitamin_a": "400% DV",
            "iron": "3mg",
            "fiber": "6g"
        },
        "health_benefits": "Chicken provides lean, easily digestible protein crucial for healing. Sweet potatoes have a medium glycemic index (63) and contain beta-carotene that converts to vitamin A for immune function and skin repair.",
        "why_needed": "Post-surgery patients require 42g of protein for muscle preservation and wound healing. The high vitamin A content (400% daily value) speeds up epithelial tissue regeneration. For diabetics, the fiber in sweet potato slows carbohydrate absorption."
    },
    "lentil_vegetable_stew": {
        "name": "Iron-Rich Lentil & Vegetable Stew",
        "type": "lunch",
        "suitable_for": ["anemia", "heart_health", "diabetes"],
        "nutritional_info": {
            "calories": 420,
            "protein": "18g",
            "iron": "6.5mg",
            "folate": "90% DV",
            "fiber": "15g"
        },
        "health_benefits": "Lentils are one of the best plant-based iron sources, providing 6.5mg per serving. The vitamin C from tomatoes and peppers enhances iron absorption. Folate supports red blood cell production.",
        "why_needed": "Essential for anemia patients - lentils provide non-heme iron that, combined with vitamin C, effectively raises hemoglobin levels. The 90% daily value of folate prevents megaloblastic anemia. High fiber (15g) benefits diabetics by improving glycemic control."
    },
    "turkey_wrap_salad": {
        "name": "Lean Turkey Wrap with Mixed Green Salad",
        "type": "lunch",
        "suitable_for": ["recovery", "heart_health"],
        "nutritional_info": {
            "calories": 450,
            "protein": "35g",
            "sodium": "420mg",
            "zinc": "4mg"
        },
        "health_benefits": "Turkey is an excellent source of lean protein with minimal saturated fat. Mixed greens provide antioxidants and phytonutrients that fight inflammation.",
        "why_needed": "Recovery patients benefit from 35g of easily digestible protein and 4mg of zinc, which activates over 300 enzymes involved in wound healing and immune response. Moderate sodium is acceptable for non-restricted diets."
    },
    "white_fish_rice": {
        "name": "Baked White Fish with Jasmine Rice",
        "type": "lunch",
        "suitable_for": ["kidney_disease", "recovery"],
        "nutritional_info": {
            "calories": 400,
            "protein": "28g",
            "potassium": "Low",
            "phosphorus": "Low",
            "sodium": "90mg"
        },
        "health_benefits": "White fish like cod or tilapia provides high-quality protein with minimal phosphorus. Jasmine rice is easily digestible and provides energy without burdening the kidneys.",
        "why_needed": "Kidney disease patients must limit potassium and phosphorus to prevent dangerous buildup in blood. This meal provides necessary protein (28g) for muscle maintenance while keeping minerals low. The low sodium (90mg) reduces kidney workload and prevents fluid retention."
    },

    # DINNER OPTIONS
    "chicken_stir_fry": {
        "name": "Chicken & Vegetable Stir-Fry with Brown Rice",
        "type": "dinner",
        "suitable_for": ["diabetes", "heart_health"],
        "nutritional_info": {
            "calories": 520,
            "protein": "36g",
            "fiber": "9g",
            "complex_carbs": "55g",
            "sodium": "380mg"
        },
        "health_benefits": "Brown rice provides sustained energy through complex carbohydrates and manganese for glucose metabolism. Colorful vegetables offer antioxidants that protect blood vessels from damage.",
        "why_needed": "Diabetics benefit from brown rice's low glycemic index (50) which prevents insulin spikes. The 9g of fiber slows digestion and improves satiety. For hypertension patients, the variety of vegetables provides potassium that naturally lowers blood pressure."
    },
    "beef_vegetable_soup": {
        "name": "Lean Beef & Vegetable Soup",
        "type": "dinner",
        "suitable_for": ["anemia", "recovery"],
        "nutritional_info": {
            "calories": 440,
            "protein": "32g",
            "iron": "4.8mg",
            "vitamin_c": "45mg",
            "zinc": "5mg"
        },
        "health_benefits": "Beef provides heme iron, which is absorbed 2-3 times more efficiently than plant-based iron. The vitamin C from vegetables maximizes iron uptake. Warm soup is easy to digest and hydrating.",
        "why_needed": "Anemia patients need the highly bioavailable heme iron (4.8mg) from beef to quickly rebuild hemoglobin stores. Combined with vitamin C, absorption rates reach 25-30%. Recovery patients benefit from 32g protein and 5mg zinc for accelerated tissue repair."
    },
    "baked_cod_vegetables": {
        "name": "Herb-Baked Cod with Roasted Vegetables",
        "type": "dinner",
        "suitable_for": ["kidney_disease", "heart_health"],
        "nutritional_info": {
            "calories": 380,
            "protein": "30g",
            "potassium": "Low",
            "phosphorus": "Low",
            "omega3": "0.5g"
        },
        "health_benefits": "Cod is a mild white fish that's kidney-friendly with minimal potassium and phosphorus. Carefully selected vegetables (like green beans and cauliflower) are low in problematic minerals.",
        "why_needed": "Kidney patients require protein (30g) for nutrition but must avoid high-potassium foods that damaged kidneys can't filter. This meal meets protein needs safely while preventing mineral buildup that could lead to bone disease or heart problems."
    },
    "turkey_meatballs_pasta": {
        "name": "Turkey Meatballs with Whole Wheat Pasta",
        "type": "dinner",
        "suitable_for": ["recovery", "diabetes"],
        "nutritional_info": {
            "calories": 500,
            "protein": "38g",
            "fiber": "8g",
            "complex_carbs": "52g"
        },
        "health_benefits": "Turkey meatballs offer complete protein with less saturated fat than beef. Whole wheat pasta has a lower glycemic index (42) than regular pasta and provides B-vitamins for energy metabolism.",
        "why_needed": "Recovery patients need sustained protein intake throughout the day - this dinner provides 38g for overnight muscle repair and immune function. Diabetics benefit from the fiber-carb combination that prevents nighttime blood sugar fluctuations."
    },
    "grilled_chicken_salad": {
        "name": "Grilled Chicken Caesar Salad (Light)",
        "type": "dinner",
        "suitable_for": ["heart_health", "recovery"],
        "nutritional_info": {
            "calories": 420,
            "protein": "35g",
            "fiber": "6g",
            "sodium": "320mg",
            "healthy_fats": "12g"
        },
        "health_benefits": "Grilled chicken provides lean protein. Romaine lettuce offers vitamin K for heart health. Light dressing uses olive oil for monounsaturated fats.",
        "why_needed": "Heart patients benefit from the low saturated fat content and healthy fats from olive oil that reduce cardiovascular inflammation. The moderate sodium (320mg) is safe for controlled hypertension. Recovery patients get 35g protein for continued healing."
    }
}

# Condition to meal type mapping
CONDITION_MEAL_MAP = {
    "Type 2 Diabetes": "diabetes",
    "Diabetes": "diabetes",
    "Anemia (Low Iron)": "anemia",
    "Anemia": "anemia",
    "Hypertension": "heart_health",
    "Post-Surgery Recovery": "recovery",
    "Surgery Recovery": "recovery",
    "Chronic Kidney Disease (Stage 3)": "kidney_disease",
    "Kidney Disease": "kidney_disease",
    "Heart Disease": "heart_health",
    "Cardiovascular Disease": "heart_health"
}

def get_suitable_meals_for_condition(condition):
    """Get meals suitable for a specific condition"""
    condition_key = CONDITION_MEAL_MAP.get(condition, "general")
    
    suitable_meals = {
        "breakfast": [],
        "lunch": [],
        "dinner": []
    }
    
    for meal_id, meal_data in MEALS.items():
        if condition_key in meal_data["suitable_for"]:
            suitable_meals[meal_data["type"]].append({
                "id": meal_id,
                "data": meal_data
            })
    
    return suitable_meals

def generate_weekly_meal_plan(patient_id):
    """Generate a 4-day meal plan for a patient with 2 options per meal"""
    patient = PATIENTS[patient_id]
    condition = patient["condition"]
    
    suitable_meals = get_suitable_meals_for_condition(condition)
    
    # Generate 4 days of meals (Today + 3 more days)
    weekly_plan = []
    days = ["Today", "Tomorrow", "Day 3", "Day 4"]
    
    for i, day in enumerate(days):
        # Get 2 different options for each meal type
        breakfast_options = []
        lunch_options = []
        dinner_options = []
        
        if len(suitable_meals["breakfast"]) >= 2:
            breakfast_options = random.sample(suitable_meals["breakfast"], 2)
        elif len(suitable_meals["breakfast"]) == 1:
            breakfast_options = [suitable_meals["breakfast"][0], suitable_meals["breakfast"][0]]
        
        if len(suitable_meals["lunch"]) >= 2:
            lunch_options = random.sample(suitable_meals["lunch"], 2)
        elif len(suitable_meals["lunch"]) == 1:
            lunch_options = [suitable_meals["lunch"][0], suitable_meals["lunch"][0]]
        
        if len(suitable_meals["dinner"]) >= 2:
            dinner_options = random.sample(suitable_meals["dinner"], 2)
        elif len(suitable_meals["dinner"]) == 1:
            dinner_options = [suitable_meals["dinner"][0], suitable_meals["dinner"][0]]
        
        day_plan = {
            "day": day,
            "date": (datetime.now() + timedelta(days=i)).strftime("%b %d, %Y"),
            "meals": {
                "breakfast": breakfast_options,
                "lunch": lunch_options,
                "dinner": dinner_options
            }
        }
        weekly_plan.append(day_plan)
    
    return weekly_plan

# ============================================================
# ROUTES - Landing Page and Login Pages
# ============================================================

@app.route('/')
def index():
    """Main landing page with 3 portals"""
    return render_template('index.html')

@app.route('/patient-login')
def patient_login_page():
    """Patient login page"""
    return render_template('patient_login.html')

@app.route('/staff-login')
def staff_login_page():
    """Staff login page"""
    return render_template('staff_login.html')

@app.route('/kitchen-login')
def kitchen_login_page():
    """Kitchen login page"""
    return render_template('kitchen_login.html')

# ============================================================
# API ENDPOINTS - Authentication
# ============================================================

@app.route('/api/patient-login', methods=['POST'])
def patient_login():
    """Patient login endpoint"""
    data = request.json
    full_name = data.get('full_name', '').strip()
    dob = data.get('dob', '').strip()
    
    # Find patient by name and DOB
    for patient_id, patient in PATIENTS.items():
        if (patient['name'].lower() == full_name.lower() and 
            patient.get('dob') == dob):
            return jsonify({
                'success': True,
                'patient_id': patient_id
            })
    
    return jsonify({
        'success': False,
        'message': 'Patient not found. Please check your name and date of birth.'
    }), 404

@app.route('/api/staff-login', methods=['POST'])
def staff_login():
    """Staff authentication endpoint"""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    # Simple authentication (in production, use proper password hashing)
    if username == 'admin' and password == 'staff123':
        return jsonify({
            'success': True,
            'message': 'Login successful'
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid username or password'
    }), 401

@app.route('/api/kitchen-login', methods=['POST'])
def kitchen_login():
    """Kitchen authentication endpoint"""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    # Simple authentication (in production, use proper password hashing)
    if username == 'chef' and password == 'kitchen123':
        return jsonify({
            'success': True,
            'message': 'Login successful'
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid username or password'
    }), 401

# ============================================================
# ROUTES - Staff and Kitchen Portals
# ============================================================

@app.route('/staff')
def staff_portal():
    """Staff portal landing page"""
    return render_template('staff_portal.html')

@app.route('/staff/patients')
def staff_patients():
    """Staff view of all patients"""
    return render_template('dashboard.html', patients=PATIENTS.values())

@app.route('/kitchen')
def kitchen_dashboard():
    """Kitchen dashboard to view and manage orders"""
    return render_template('kitchen_dashboard.html')

# ============================================================
# ROUTES - Patient Portal
# ============================================================

@app.route('/patient/<patient_id>/meals')
def patient_meals(patient_id):
    """Patient meal selection page"""
    if patient_id not in PATIENTS:
        return "Patient not found", 404
    
    patient = PATIENTS[patient_id]
    meal_plan = generate_weekly_meal_plan(patient_id)
    
    return render_template('patient_detail.html', patient=patient, meal_plan=meal_plan)

@app.route('/patient/<patient_id>')
def patient_detail(patient_id):
    """Individual patient meal plan page"""
    if patient_id not in PATIENTS:
        return "Patient not found", 404
    
    patient = PATIENTS[patient_id]
    meal_plan = generate_weekly_meal_plan(patient_id)
    
    return render_template('patient_detail.html', patient=patient, meal_plan=meal_plan)

@app.route('/patient/<patient_id>/orders')
def patient_orders(patient_id):
    """View patient orders with tracking"""
    if patient_id not in PATIENTS:
        return "Patient not found", 404
    
    patient = PATIENTS[patient_id]
    patient_order_list = [order for order in ORDERS if order['patient_id'] == patient_id]
    
    return render_template('patient_orders.html', patient=patient, orders=patient_order_list)

# ============================================================
# ROUTES - Admin Functions
# ============================================================

@app.route('/add-patient')
def add_patient_page():
    """Page to add new patient"""
    return render_template('add_patient.html')

@app.route('/api/add-patient', methods=['POST'])
def add_patient():
    """API endpoint to add new patient and auto-generate meal plan"""
    data = request.json
    
    # Validate name (letters only)
    import re
    if not re.match(r'^[A-Za-z\s]+$', data["name"]):
        return jsonify({
            "success": False,
            "message": "Name must contain only letters"
        }), 400
    
    # Generate new patient ID
    existing_ids = [int(p[1:]) for p in PATIENTS.keys()]
    new_id = f"P{str(max(existing_ids) + 1).zfill(3)}"
    
    # Random avatar color
    colors = ["#FF6B9D", "#4ECDC4", "#95E1D3", "#FFE66D", "#A8E6CF", "#F38181", "#AA96DA", "#FCBAD3"]
    
    # Create new patient
    new_patient = {
        "id": new_id,
        "name": data["name"],
        "age": int(data["age"]),
        "dob": data.get("dob", ""),
        "condition": data["condition"],
        "dietary_needs": data.get("dietary_needs", []),
        "restrictions": data.get("restrictions", []),
        "avatar_color": random.choice(colors)
    }
    
    PATIENTS[new_id] = new_patient
    
    # Generate meal plan
    meal_plan = generate_weekly_meal_plan(new_id)
    
    return jsonify({
        "success": True,
        "patient_id": new_id,
        "patient": new_patient,
        "meal_plan": meal_plan
    })

@app.route('/api/patients')
def get_patients():
    """API endpoint to get all patients"""
    return jsonify(list(PATIENTS.values()))

# ============================================================
# API ENDPOINTS - Orders
# ============================================================

@app.route('/api/place-order', methods=['POST'])
def place_order():
    """Place a meal order"""
    data = request.json
    
    order = {
        'id': str(uuid.uuid4()),
        'patient_id': data['patient_id'],
        'patient_name': data['patient_name'],
        'meal_name': data['meal_name'],
        'meal_type': data['meal_type'],
        'day': data['day'],
        'status': 'pending',
        'order_time': datetime.now().isoformat(),
        'accepted_time': None,
        'in_progress_time': None,
        'completed_time': None,
        'estimated_completion': (datetime.now() + timedelta(minutes=30)).isoformat()
    }
    
    ORDERS.append(order)
    
    return jsonify({
        'success': True,
        'order': order
    })

@app.route('/api/orders')
def get_orders():
    """Get all orders for kitchen dashboard"""
    return jsonify(ORDERS)

@app.route('/api/orders/<order_id>/status', methods=['POST'])
def update_order_status(order_id):
    """Update order status"""
    data = request.json
    new_status = data.get('status')
    
    for order in ORDERS:
        if order['id'] == order_id:
            order['status'] = new_status
            
            if new_status == 'accepted':
                order['accepted_time'] = datetime.now().isoformat()
            elif new_status == 'in_progress':
                order['in_progress_time'] = datetime.now().isoformat()
            elif new_status == 'completed':
                order['completed_time'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'order': order
            })
    
    return jsonify({'success': False, 'message': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
