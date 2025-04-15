from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights

import streamlit as st
    
if 'page' not in st.session_state:
    st.session_state.page = "page1"  
    st.session_state.ticker = "RELIANCE"  
    st.session_state.market = "BSE" 
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False



def page1():
    st.title('Stock AI Agent')

    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.ticker = st.text_input("Enter Stock Ticker Symbol", value=st.session_state.ticker, key="ticker_input")  #Use key for unique input.
    with col2:
        st.session_state.market = st.selectbox("Select Market", ["BSE", "NASDAQ"], index=["BSE", "NASDAQ"].index(st.session_state.market), key="market_input") #Use key, corrected index.

    
    st.sidebar.header("About")
    st.sidebar.write("This is a stock analysis platform.")

    
    st.markdown("---")

    if st.button('Submit'):
        st.session_state.page = "page2"  # Go to the next page
        st.session_state.internal_results_available = False
        st.rerun() 

def page2():


    st.title(f"Analysis for {st.session_state.ticker} ({st.session_state.market})")  # Use stored inputs
    stock=st.session_state.ticker
    market=st.session_state.market
    if not st.session_state.internal_results_available:
        with st.spinner('Analyzing... Please wait...'):
            image_path = f"images/{market}_{stock}.png"

            st.session_state.image_path=image_path
            
            stock_api_obj = StockAPI("FIWYBPGXYIL7SKH2")

            market_data=stock_api_obj.get_stock_info(stock,market)

            stock_analyzer_obj=StockAnalyzer()

            df=stock_analyzer_obj.json_to_dataframe(market_data,stock, market)

            stock_analyzer_obj.plot_stock_data(df,stock, market,image_path)

            ai_insights_obj=AIInsights("AIzaSyBjwL3RxwL7HhTIYs60jgOdircNmK1Y_zY")

            response=ai_insights_obj.get_ai_insights(image_path,stock,market)

            candidates = response.candidates  
            for candidate in candidates:
                text_parts = candidate.content.parts
                for part in text_parts:
                    print(part.text)
                    st.session_state.ai_insights += part.text   
            st.session_state.internal_results_available = True
        
    if  st.session_state.internal_results_available:
        st.subheader("Chart Analysis")
        st.image(st.session_state.image_path, caption=f"{st.session_state.ticker} Chart",use_column_width=True)  # Example image

        st.subheader("Analysis Results")
        st.write(st.session_state.ai_insights)
        
        if st.button("Back"): #Back button
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.rerun()


if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()