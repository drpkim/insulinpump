import streamlit as st
import hydralit_components as hc 
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

#apply customized info card with
theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange', 'icon_color': 'orange', 'icon': 'fa fa-star-of-life'}
theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-syringe'}
theme_ok = {'bgcolor': '#e8e6f7', 'title_color': 'purple', 'content_color': 'purple', 'icon_color': 'purple', 'icon': 'fa fa-utensils'}

st.markdown('# Type 1 Diabetes Insulin Pump and Bolus Calculator Protocol')
st.caption("Created by Phillip Kim, MD, MPH, Last update: 12/5/22")

st.write('NOTE: intended for professional usage only')

wt_carb_ratio = 0
m1_carb_ratio = 0
isf = 0
basal_rate = 0 

#determine total insulin dosage, 24h rate, and fixed meal bolus amount
def dosage (tdd, rate=bool, fixed=bool):
    if rate:
        return round((tdd/2)/24, 1)
    if fixed:
        fixed_dosage = round((tdd/2)/3)
        return st.info(f"Fixed insulin per meal (3): **{fixed_dosage} units**"),st.caption("**About Fixed Dosage:**  Fixed Bolus: 1⁄2 Pump tDD ÷ 3 (equal meals). Use for patients who are not yet carbohydrate counting, or who have lower cognitive ability. Convert fixed units per meal to fixed grams of carbohydrate per meal and provide dosing instructions for small, medium and large meals.")
    else:
        return round(tdd/2, 1)
    
def carb_ratio (tdd):
    global wt_carb_ratio
    wt_carb_ratio = round((st.session_state.weight*2.8)/tdd)
    global m1_carb_ratio
    m1_carb_ratio = round(450/tdd)
    if st.session_state.weight:
        return m1_carb_ratio, st.info(f"Method 1 using 450 RULE: **{m1_carb_ratio} g/unit insulin**"), st.caption("**About Method 1:** Carb ration = 450 ÷ by the Pump tDD"), st.info(f"Alternative using weight: **{wt_carb_ratio} g/unit insulin**"), st.caption("**About Alternative:** Carb ratio = lbs. x 2.8 ÷ Pump tDD")
    else:
        return st.info(f"Method 1 using 450 RULE: **{m1_carb_ratio} g/unit insulin**"), st.caption("**About Method 1:** 450 ÷ by the Pump tDD = Carbohydrate ratio")
      

def correction_factor (tdd):
    st.markdown("#### Insulin Sensitivity Factor (ISF)/Correction Bolus")
    global isf
    isf = round(1700/tdd)
    return isf, st.error(f"Senitivity Factor 1700 Rule: **{isf} mg/dL/unit insulin**")

insulin_pump, quick_bolus, summary = st.tabs(['Calculate Inital Pump Settings', 'Quick Bolus Calculator', 'Summary Sheet'])

def active_insulin_amount (basal_rate = 0.0, active_time = 0):
    iob = 0 
    for a in range (1, active_time+1):
        iob += basal_rate * (a/active_time)
    return iob 



#INSULIN PUMP CALCULATION TAB
with insulin_pump:
    st.number_input(label="Prepump Total Daily Dose", key='pre_pump', min_value=0, max_value=500, step=1)
    st.number_input(label="Weight (lbs)", key='weight', min_value=0.0, max_value=500.0,)


    #wt is in lbs
    pump_tdd = round(st.session_state.pre_pump * 0.75, 1)
    wt_tdd = round(st.session_state.weight * 0.23, 1) 
    avg_tdd = 0.0
    if pump_tdd and wt_tdd:
        avg_tdd = round((pump_tdd+wt_tdd)/2, 1)


    if st.session_state.pre_pump and not st.session_state.weight:
        "### Pump Total Daily Dose (tDD):"
        st.success(f"Method 1 using pre-pump TDD: **{pump_tdd} units/day**") 
        st.caption("**About Method 1:**  tDD = pre-pump TDD x 0.75; Reduce Pre-Pump by 25% or less if pre-pump TDD >70%")
        "#### Total Basal Daily Dosage "
        basal_rate = dosage(pump_tdd, False, False)
        st.warning(f"**{basal_rate} units/day (total daily basal insulin)**")
        st.caption("Divide Insulin Pump TDD in half using pre-pump TDD")

        '#### Starting Hourly Basal Rate'
        st.warning(f"**{dosage(pump_tdd, True, False)} units/hr**")
        st.caption("Divide Total Insulin Pump Basal Requirement by 24 hours")
        '#### Carbohydrate Ratio/Meal Bolus'
        cr = carb_ratio(pump_tdd)
        #Correction Factor
        dosage(pump_tdd, False, True)
        correct_fact=correction_factor(pump_tdd)
        st.caption("ISF = 1700 ÷ pre-pump tDD")

    if st.session_state.weight and not st.session_state.pre_pump:
        "### Pump Total Daily Dose (tDD):"
        st.success(f"Method 2 using weight: **{wt_tdd}** units/day")
        st.caption("**About Method 2:** lbs. x 0.23 = Pump tDD")
        "#### Total Basal Daily Dosage"
        st.warning(f"**{dosage(wt_tdd, False, False)} units/day (total daily basal insulin)**")
        st.caption("Divide Insulin Pump TDD in half using weight based")
        '#### Starting Hourly Basal Rate'
        basal_rate = dosage(wt_tdd, True, False)
        st.warning(f"**{basal_rate} units/hr**")
        st.caption("Divide Total Insulin Pump Basal Requirement by 24 hours")
        '#### Carbohydrate Ratio/Meal Bolus'
        carb_ratio(wt_tdd)
        dosage(wt_tdd, False, True)
        correct_fact=correction_factor(wt_tdd)
        st.caption("ISF = 1700 ÷ weight based tDD")

    if st.session_state.pre_pump and st.session_state.weight:
        "### Pump Total Daily Dose (tDD):"
        st.success(f"Method 1 using pre-pump TDD: **{pump_tdd} units/day**")
        st.caption("**About Method 1:**  tDD = pre-pump TDD x 0.75; Reduce Pre-Pump by 25% or less if pre-pump TDD >70%")
        st.success(f"Method 2 using weight: **{wt_tdd}** units/day")
        st.caption("**About Method 2:** lbs. x 0.23 = Pump tDD") 

        #calculate average
        st.success(f"Average of pre-pump TDD and weight based: **{avg_tdd}** units/day")
        st.caption("Use both methods and AVERAGE the two values to determine the starting insulin pump TDD \n\nExample: (40 units/day + 35 units/day) ÷ 2 = 37.5 units/day Insulin Pump Total Daily Dose\n\n• For hypoglycemia or hypoglycemia unawareness, use the lower value\n\n• For consistent hyperglycemia, an elevated A1C, or in pregnancy, use the higher value\n\n• For erratic glucose control, or if starting insulin pump therapy at diagnosis or from oral medications, use the weight-based method")

        "#### Total Basal Daily Dosage"
        st.warning(f"**{dosage(avg_tdd, False, False)} units/day (total daily basal insulin)**")
        st.caption("Divide half using average pre-pump TDD and weight based")
        '#### Starting Hourly Basal Rate'
        basal_rate = dosage(avg_tdd, True, False)
        st.warning(f"**{basal_rate} units/hr**") 
        st.caption("Divide Total Insulin Pump Basal Requirement by 24 hours")
        '#### Carbohydrate Ratio/Meal Bolus'
        carb_ratio(avg_tdd)
        dosage(avg_tdd, False, True)
        correct_fact=correction_factor(avg_tdd)
        st.caption("ISF = 1700 ÷ average of pre-pump and weight based tDD")
    
    """**Instruction for Adjustments**
    
    • If nocturnal, fasting/pre-meal or bedtime BG > target, increase basal 10–20%
    • If nocturnal, fasting/pre-meal or bedtime BG < target, decrease basal 10–20%
    • If post-meal BG > 60mg/dL above pre-meal BG, decrease carb ratio by 10–20%
    • If post-meal BG < 30mg/dL above pre-meal BG, increase carb ratio by 10–20%
    
    Elevated BG: Verify trends 2–3 days before adjusting 
    Low BG: Consider immediate adjustment
    """    

        
    # else:
    #     st.error("Sorry, missing values", icon='😲')

    
    "**Refrence/Resources**"   

    st.markdown("1. Bruce W. Bode, MD, FACE, Pumping ProtocoL: A Guide to Insulin Pump therapy Initiation. Includes an introduction to continuous glucose monitoring (CGM) and therapy management software. 2008.\n2. Boardman S, Greenwood R, Hammond P, on behalf of the Association of British Clinical Diabetologists (ABCD). ABCD position paper on insulin pumps. Practical Diabetes International. 2007;78(2):149-158.\n3. Medical management of type 1 diabetes. In: Bode BW, ed. Tools of Therapy – Insulin Treatment. 4th ed. American Diabetes Association; 2004;64-68.\n")
    
#QUICK BOLUS
with quick_bolus: 
    carbs = st.number_input("**Enter carb units (g)**", min_value=0, step=1, key='carbs')
    qicr = st.number_input("**Enter carb ratio**", min_value=0, step=1, value=m1_carb_ratio, key='qicr', help='Default value using 450 carb ratio rule')
    qisf = st.number_input("**Enter insulin correction factor (mg/dL/unit)**", min_value=0, step=1,value = isf, key="qisf")
    target_bg = st.number_input("**Enter target Blood Gluose (mg/dL)**", min_value=80, max_value=180, step=1, key='target_bg')

    
    with st.expander(label="**Suggested Starting Target Range Settings**"):
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.write("### Awareness Level")
            st.write("Normal Awareness")
            st.write("Hypoglycemia Unawareness")
            st.write("Pregnancy")
        with col2:
            st.write("### Daytime")
            st.write("90-100 mg/dL")
            st.write("100-100 mg/dL")
            st.write("80-90 mg/dL")
        with col3:
            st.write("### Nighttime")
            st.write("100-120 mg/dL")
            st.write("110-120 mg/dL")
            st.write("90-100 mg/dL")
        st.info("\n\nIf the BG is **above** target → Additional insulin is calculated\n\nIf the BG is **within** target → No additional insulin is calculated\n\nIf the BG is **below** target → Insulin is subtracted from the meal bolus")
    active_insulin = st.selectbox("**Select Active Insulin Time**", options=(3, 4, 5))
    with st.expander(label="**Suggested Active Insulin Time**"):
        col1, col2, col3 = st.columns(3)
        st.caption("Note: Active Insulin is the amount of insulin remaining in the body from previous boluses that continues to have a pharmacodynamic effect and the potential to lower glucose levels. Active Insulin Time is the length of time the Bolus Wizard® calculator tracks active insulin following a bolus dose. Can be set from two to eight hours.\n\nInsulin On Board (IOB) = Σ (Basal rate * (n+i/active time)\n\nExample for 4 hours active insulin time with 1u/hr basal: IOB = 1x1/4 + 1x2/4+ 1x3/4 + 1x4/4 = 2.5 units IOB")
        with col1:
            st.write ('### Adults')
            st.write("4-5 hours")
        with col2:
            st.write ('### Children')
            st.write("4-5 hours")
        with col3:
            st.write ('### Pregnancy')
            st.write("3-4 hours")
    glucose_read = st.number_input(label="Enter current glucose reading (mg/dL)", min_value=0, max_value=800, step=1)

    #BOLUS CACULATION
    #food bolus
    #declare variable
    insulin_carbs=0
    correction_carbs=0
    correct_insulin=0

    if carbs and qicr:
        insulin_carbs = round(carbs/qicr)
    if not carbs:
        insulin_carbs = 0 
        
    if qisf and glucose_read:
        correction_carbs = glucose_read - target_bg
        correct_insulin = round(correction_carbs/qisf, 1)
        
    iob = round(active_insulin_amount(basal_rate=basal_rate, active_time=active_insulin), 1)
    
    suggest_correction = round((correct_insulin - iob), 1)
    
    total_bolus = round((insulin_carbs+suggest_correction), 1)
    
    if total_bolus <= 0:
        total_bolus = "N/A"
 
        
        
    col1, col2, col3 = st.columns(3)
    with col1:
        #st.metric(label="Recommended Correction (units)", value=suggest_correction)
        hc.info_card(title="Recommended Correction (units)", content=suggest_correction, theme_override=theme_neutral, title_text_size= "1rem", content_text_size="2rem")
    with col3:
        #st.metric(label="**Total Insulin (units)**", value=round((insulin_carbs+suggest_correction), 1))
        hc.info_card(title="Total Insulin Required (units)", content=total_bolus, theme_override=theme_good, title_text_size= "1rem", content_text_size="2rem")
    with col2:
        #st.metric(label="Food Bolus Insulin (units)", value=insulin_carbs)
        hc.info_card(title="Food Bolus Insulin (units)", content=insulin_carbs, theme_override=theme_ok, title_text_size= "1rem", content_text_size="2rem")
    
    """**Formula**
    
    Correction Dose = (Current BG - Target BG)/ISF 
    EXAMPLE:
    Blood Glucose Target = 100 mg/dL
    Insulin Sensitivity Factor = 45 mg/dL
    • If BG is above target:
        A positive correction dose is calculated BG = 160 mg/dl: 
        (160 - 100) ÷ 45 = 1.3 units
    • If BG is below target:
        A negative correction is calculated and 
        subtracted from the meal bolus BG = 60 mg/dl: 
        (60 - 100) ÷ 45 = - 0.9 units
    
    Important points:
    • IOB must be defined and accounted into correction inuslin units 
    • Recommended correction insulin = Active insulin units - correction units

    Food Bolus Amount:
    • Food Bolus unit = Food (g) * Carb ratio (u/g)

    Total Estimated Bolus:
    • Total bolus units = Food Bolus unit + Suggested correction insulin

    """

def age(birthdate):
    # Get today's date object
    today = date.today()
    
    # A bool that represents if today's day/month precedes the birth day/month
    one_or_zero = ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    # Calculate the difference in years from the date object's components
    year_difference = today.year - birthdate.year
    
    # The difference in years is not enough. 
    # To get it right, subtract 1 or 0 based on if today precedes the 
    # birthdate's month/day.
    
    # To do this, subtract the 'one_or_zero' boolean 
    # from 'year_difference'. (This converts
    # True to 1 and False to 0 under the hood.)
    age = year_difference - one_or_zero
    
    return age
   
#SUMMARY SHEET
with summary:
    col1, col2 = st.columns(2)
    with col1:
        first = st.text_input ("First Name")
        dob = st.date_input('DOB', min_value=datetime.date.today()-relativedelta(years=100), max_value=datetime.date.today())
    with col2:
        last = st.text_input ("Last Name")
        mr_num = st.text_input("MR#")
    st.code(f"""
    Name: {' '.join([first, last])}\nDOB: {dob}\nAge: {age(dob)}\nMR: {mr_num}\n\n#Total Daily Dose\nTDD wt based: {wt_tdd} units\nTDD pre-pump based {pump_tdd} units\nTDD avg based: {avg_tdd} units\n\n#Basal Dosage and 24h-Rate\nUsing pre-pump TDD: {dosage(pump_tdd, False, False)} units/day or {dosage(pump_tdd, True, False)} u/hr\nUsing weight based TDD: {dosage(wt_tdd, False, False)} units/day or {dosage(wt_tdd, True, False)} u/hr\nUsing average TDD: {dosage(avg_tdd, False, False)} units/day or {dosage(avg_tdd, True, False)} u/hr\n\n#Carb Ratio\nCarb ratio 450 method: {m1_carb_ratio} g/unit\nCarb ratio based on wt: {wt_carb_ratio} g/unit\n\n#Correction Factor\n1700 Rule: {isf} mg/dL/unit\n\n#Active Insulin and Time\nAmount: {iob} units\nTime: {active_insulin} hrs
    """)

 
