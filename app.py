import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

#page configration
st.set_page_config(
    page_title="Car Price Prediction",
    page_icon="",
    layout="wide"
)

#custom css
st.markdown("""
            <style>
            .main{padding:0rem 1rem;}
            h1{color: #e74c3c; padding-bottom:1rem;}
            </style>
            
             """,unsafe_allow_html=True)

#load model
@st.cache_resource
def load_model():
    try:
        model=joblib.load("car_prediction_model.pkl")
        return model
    except FileNotFoundError:
        return None
    
    
    
    
#header 
st.title("Car Price Prediction System")
st.markdown("### Get an instant AI-powered valuation for your used car")



#load model
model = load_model()

if model is None:
    st.error("** model file not found **")
    st.info("""
    Please run the following command first 
    '''
    python car_price_prediction.py
    '''
    This will train and save the model.
    """)
    st.stop()
    
    
# Sidebar input
st.sidebar.title("Car Details") 
st.sidebar.subheader("Manufacturing Year")
year = st.sidebar.slider("Manufacturing Year", 2000, 2024, 2015)

present_price=st.sidebar.number_input("current Ex - Showroom price(lakhs)",0.0,50.0,5.0,0.1) 

kms_driven=st.sidebar.number_input("Kilometer Driven ",0,500000,50000,1000)

st.sidebar.subheader("Car Specification")
Fuel_Type=st.sidebar.selectbox("Fuel Type",["Petrol","Diesel","CNG"])
Seller_Type=st.sidebar.selectbox("Seller Type",["Dealer","Individual"])
Transmission=st.sidebar.selectbox("Transmission",["Manual","Automatic"])
Owner = st.sidebar.selectbox("number of previous owners", [0,1,2,3])


#calculate car age
Current_year = 2026 
car_age=Current_year - year

# Calculate car age
st.sidebar.markdown("---")
predict_btn=st.sidebar.button(" Get Price Estimate",type= "primary",use_container_width=True)


#main content
if predict_btn:
    # Encode categorical
    Fuel_encoded={"Petrol":0,"Diesel":1,"CNG":2}[Fuel_Type]
    Seller_encoded={"Dealer":0,"Individual":1}[Seller_Type]
    Transmission_encoded={"Manual":0,"Automatic":1}[Transmission]
    
    #prepare input 
    input_data=pd.DataFrame({
        "Year":[year],
        "Present_Price":[present_price],
        "Kms_Driven":[kms_driven],
        "Fuel_Type":[Fuel_encoded],
        "Seller_Type":[Seller_encoded],
        "Transmission":[Transmission_encoded],
        "Owner":[Owner]
    }) 
    
    #make prediction
    predicted_price = model.predict(input_data)[0]
    
    #calculate result
    depreciation =present_price-predicted_price
    depreciation_percent =(depreciation/present_price)*100 if present_price>0 else 0

    
    
    #display result
    st.markdown("---")
    st.header(" Price Estimation Result")


    #main metrics
    col1,col2,col3 = st.columns(3)

    
    
    with col1:
         st.metric(
             
             "Estimated Selling Price",
             f"₹{predicted_price :.2f} Lakhs",
             delta=None
         )    
    
    with col2:
         st.metric(
             "Current Showroom Price",
             f"₹{present_price :.2f} Lakhs",
             delta=None
    
        )
    
    with col3:
         st.metric(
             "Total Depreciation",
             f"₹{depreciation:.2f} Lakhs",
             delta=f"{depreciation_percent:.1f}%"
         ) 
    
    
    # gauge chart for price range
    st.markdown("---")
    st.subheader("Price Analysis")

    col1,col2 = st.columns([2,1])   

    
    with col1:
        #price range estimate(10%)
        lower_estimate=predicted_price*0.9
        upper_estimate=predicted_price*1.1
        
        st.success(f"""
        **Expected Price Range:** ₹{lower_estimate:.2f}L  —  ₹{upper_estimate:.2f}L
        
        This is the typical market range for similar vehicles.           
                   
        """)
        
        #price breakdown
        st.write("** Price factor:**")
        
        factors=[]
        
        if car_age <=2:
            factors.append("Very new car - minimal depreciation")
        elif car_age <5:
            factors.append("Relatively new - good resale value")
        elif car_age <=10:
            factors.append("Moderate age - average market value")
        else:
            factors.append("Older car - higher depreciation")
            
        if kms_driven <=30000:
            factors.append("Low mileage - adds value")
        elif kms_driven <=80000:
            factors.append("Average mileage ")
        else:
            factors.append("High mileage - reduces values")
            
        if Transmission=="Automatic":
            factors.append("Automatic Transmission - premium pricing")      
        if Fuel_Type == "Diesel":
            factors.append("Diesel - preferred for high usage")
        elif Fuel_Type == "Petrol":
            factors.append("Petrol - standard option")
            
        if Seller_Type == "Dealer":
            factors.append("Dealer - may offer better warranty")
            
        for factor in factors:
            st.markdown(f"- {factor}")
            
            
    with col2:
        #gauge chart
        max_price = max(present_price * 1.2, 1)

        fig = go.Figure (go.Indicator(
            mode="gauge+number",
            value = predicted_price,
            title = {"text":"Estimated price"},
            number = {"prefix":"₹","suffix":"L"},
            gauge={
                "axis": {"range":[None,max_price]},
                "bar":{"color":"#e74c3c"},
                "steps":[
                    {"range":[0,present_price*0.3],"color":"lightgray"},
                    {"range":[present_price*0.3,present_price*0.7],"color":"lightyellow"},
                    {"range":[present_price*0.7,max_price],"color":"lightgreen"},
                ],
                "threshold":{
                    "line":{"color":"blue","width":4},
                    "thickness":0.75,
                    "value": present_price
                }
            }
        )) 
        fig.update_layout(height=300,margin=dict(l=20,r=20,t=50,b=20))
        st.plotly_chart(fig,use_container_width=True)  
        
    # car details summary
    st.markdown("---")
    st.subheader(" Your Car Details")
    
    details_col1,details_col2=st.columns(2)
    
    with details_col1:
        st.write(f"**manufacturing year:**{year}")
        st.write(f"**car age:**{car_age}years")
        st.write(f"**kilometer driven:**{kms_driven}km")
        st.write(f"**fuel type:**{Fuel_Type}")
        
    with details_col2:
        st.write(f"**transmission:**{Transmission}")
        st.write(f"**seller type:**{Seller_Type}")
        st.write(f"**Current Showroom Price:**₹{present_price}Lakhs")
        
    #tips for selling
    st.markdown("---")
    st.subheader("Tips To Get Better Price")
    
else:
    #initial page
    st.markdown("---")  
    st.info(" Enter Your Car Details in the Side Bar and Click ** Get Price Estimate")   
    
    # show example car
    st.subheader(" Example Valuations")
    
    col1,col2,col3 = st.columns(3)
    
    with col1:
        st.write("** Recent car **")
        st.write("Year:2024")
        st.write("Price:₹8.5L")
        st.write("Kms:20,000")
        st.write("Est:₹6.5-7.5L")  
        
    with col2:
        st.write("** Mid- Range Car**")
        st.write("Year:2015")
        st.write("Price:₹6.0L")
        st.write("Kms:50,000")
        st.write("Est:₹3.5-4.5L")   
             
    with col3:
        st.write("** Older Car **")
        st.write("Year:2010")
        st.write("Price:₹5.0L")
        st.write("Kms:100,000")
        st.write("Est:₹1.5-2.5L")  
        
    st.markdown("---")
    #model info
    st.subheader("Model Information")
    col1,col2,col3=st.columns(3)
    col1.metric("Algorithm","ML Regression")
    col2.metric("Accuracy","~85%")
    col3.metric("Dataset","300+car")    
        
        
            
        
        
                 
                        
            
                                            
    
       
