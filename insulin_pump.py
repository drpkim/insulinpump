import streamlit as st
import hydralit_components as hc 

#apply customized info card with 
theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange', 'icon_color': 'orange', 'icon': 'fa fa-star-of-life'}
theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-syringe'}
theme_ok = {'bgcolor': '#e8e6f7', 'title_color': 'purple', 'content_color': 'purple', 'icon_color': 'purple', 'icon': 'fa fa-utensils'}

st.markdown('# Type 1 Diabetes Insulin Pump and Bolus Calculator Protocol')
st.write('NOTE: intended for professional usage only')

wt_carb_ratio = 0
m1_carb_ratio = 0
isf = 0

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
        return m1_carb_ratio, st.info(f"Method 1 using 450 RULE: **{m1_carb_ratio} g/unit insulin**"), st.caption("**About Method 1:** 450 ÷ by the Pump tDD = Carbohydrate ratio"), st.info(f"Method 2 using weight: **{wt_carb_ratio} g/unit insulin**")
    else:
        return st.info(f"Method 1 using 450 RULE: **{m1_carb_ratio} g/unit insulin**"), st.caption("**About Method 1:** 450 ÷ by the Pump tDD = Carbohydrate ratio")
      

def correction_factor (tdd):
    st.markdown("#### Insulin Sensitivity Factor (ISF)/Correction Bolus")
    global isf
    isf = round(1700/tdd)
    return st.error(f"Senitivity Factor 1700 Rule: **{isf} mg/dL/unit insulin**")

insulin_pump, quick_bolus = st.tabs(['Calculate Inital Pump Settings', 'Quick Bolus Calculator'])
#INSULIN PUMP CALCULATION TAB
with insulin_pump:
    st.number_input(label="Prepump Total Daily Dose", key='pre_pump', min_value=0, max_value=500, step=1)
    st.number_input(label="Weight (lbs)", key='weight', min_value=0.0, max_value=500.0,)


    #wt is in lbs
    pump_tdd = round(st.session_state.pre_pump * 0.75, 1)
    wt_tdd = round(st.session_state.weight * 0.23, 1) 
    avg_tdd = round((pump_tdd+wt_tdd)/2, 1)


    if st.session_state.pre_pump and not st.session_state.weight:
        "### Pump Total Daily Dose (tDD):"
        st.success(f"Method 1 using pre-pump TDD: **{pump_tdd} units/day**") 
        st.caption("**About Method 1:**  Reduce Pre-Pump by 25% or less if pre-pump TDD >70%")
        "#### Total Basal Daily Dosage "
        st.warning(f"**{dosage(pump_tdd, False, False)} units/day (total daily basal insulin)**")
        '#### Starting Hourly Basal Rate'
        st.warning(f"**{dosage(pump_tdd, True, False)} units/hr**")
        '#### Carbohydrate Ratio/Meal Bolus'
        cr = carb_ratio(pump_tdd)
        dosage(pump_tdd, False, True)
        correction_factor(pump_tdd)

    if st.session_state.weight and not st.session_state.pre_pump:
        "### Pump Total Daily Dose:"
        st.success(f"Method 2 using weight: **{wt_tdd}** units/day")
        st.caption("**About Method 2:** lbs. x 0.23 = Pump tDD")
        "#### Total Basal Daily Dosage"
        st.warning(f"**{dosage(wt_tdd, False, False)} units/day (total daily basal insulin)**")
        '#### Starting Hourly Basal Rate'
        st.warning(f"**{dosage(wt_tdd, True, False)} units/hr**")
        '#### Carbohydrate Ratio/Meal Bolus'
        carb_ratio(wt_tdd)
        dosage(wt_tdd, False, True)
        correction_factor(wt_tdd)

    if st.session_state.pre_pump and st.session_state.weight:
        "### Pump Total Daily Dose:"
        #calculate average
        st.success(f"Average of pre-pump TDD and weight based: **{avg_tdd}** units/day")
        "#### Total Basal Daily Dosage"
        st.warning(f"**{dosage(avg_tdd, False, False)} units/day (total daily basal insulin)**")
        '#### Starting Hourly Basal Rate'
        st.warning(f"**{dosage(avg_tdd, True, False)} units/hr**") 
        '#### Carbohydrate Ratio/Meal Bolus'
        carb_ratio(avg_tdd)
        dosage(avg_tdd, False, True)
        correction_factor(wt_tdd)
        
    # else:
    #     st.error("Sorry, missing values", icon='😲')

    """****Formula****\n    
    Estimated basal rate based on wt (kg)
    (0.5 x kg)/2 * 1/24

    Estimated basal rate based on TDD 
    (0.75 x TDD)/2 * 1/24

    Bolus Insulin
    CIR-= 450 / TDD

    Correction Factor 
    Insulin Sensitivity Factor  (Correction Factor)  = 1700 / TDD

    """


#QUICK BOLUS
with quick_bolus: 
    carbs = st.number_input("**Enter carb units (g)**", min_value=0, step=1, key='carbs')
    qicr = st.number_input("**Enter carb ratio**", min_value=0, step=1, value=m1_carb_ratio, key='qicr', help='Default value using 450 carb ratio rule')
    qisf = st.number_input("**Enter insulin correction factor (mg/dL/unit)**", min_value=0, step=1, value = isf, key="qisf")
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
        correct_insulin = round(correction_carbs/qisf)
        
    active_insulin_amount = round((active_insulin * 0.32), 1)
    suggest_correction = round((correct_insulin - active_insulin_amount), 1)
    col1, col2, col3 = st.columns(3)
    with col1:
        #st.metric(label="Recommended Correction (units)", value=suggest_correction)
        hc.info_card(title="Recommended Correction (units)", content=suggest_correction, theme_override=theme_neutral, title_text_size= "1rem", content_text_size="2rem")
    with col3:
        #st.metric(label="**Total Insulin (units)**", value=round((insulin_carbs+suggest_correction), 1))
        hc.info_card(title="Total Insulin Required (units)", content=round((insulin_carbs+suggest_correction), 1), theme_override=theme_good, title_text_size= "1rem", content_text_size="2rem")
    with col2:
        #st.metric(label="Food Bolus Insulin (units)", value=insulin_carbs)
        hc.info_card(title="Food Bolus Insulin (units)", content=insulin_carbs, theme_override=theme_ok, title_text_size= "1rem", content_text_size="2rem")

