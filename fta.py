import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth, exceptions
import pandas as pd
from datetime import date, timedelta
import plotly.express as px

# Set the page to wide layout at the very beginning of the script
st.set_page_config(layout="wide")

# This script is a complete Personal Finance Tracker application with
# Firebase Authentication for multi-user support, Firestore for data storage,
# and various visualization and analysis features.

# --- Firebase Setup (MANDATORY) ---
# Replace this with your actual Firebase project configuration.
# You can get this from your Firebase project settings.
firebase_config = {
  "type": "service_account",
  "project_id": "finance-tracker-nik",
  "private_key_id": "5d24bcf78d496a7e7c6adb574b3ae3e7b1807563",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDAb87HM9vN7mMh\nkEV/c69F+RfxqiGFdpt56ym+80qBsBUfl7bO4nbIHrT8FkaW9C222p5j/tFJaXMb\no2QYvjRfZg0XKot+CJ70Jh6HAIyLhMD7afJ/Meo5VxHgTN44DU4YPbH94x5uQX8l\nC7BdLrGp5aslPQ9IfiBfDNdTd1Mkjpn2WwtaBVvrNLE4IvpMhO1PI17mkv7wRjgO\nUB+yteRRKryWufoZufSGQ2gFsVQQRg5mzANfUD+hWiDNWrZNptT3IVkKKUQlxBIT\nbtuzxbhCwlpEu0aoJGEwo2EdCYYp5z7XB4WrnxlQEm1dOT5ouYd8ByFa9GNvLfW6\nYEbCiezPAgMBAAECggEAGcnB9ZsC/T1Rholtbs+DcQaZCVcpx9dlrXhwrziuRuPg\naMvtgRsDHP1UdqXLjuYpDCSO7kqTJFnfxZfnTZOLtC8aWPzoFZs1JfXHyIKv0vCW\n5fpEN3xqbYW4DQ1wCCXsTb5S0HmztcXMMpw25b3grCptfX+JwUa5stMnNfW7LB4+\ncuX6RX/vHMRT1Xr1N5ZcAHfli0X9JCGqv2a5znbFoMOzYIl5uhY5c+fecWv1xW1I\nlDF3IIW3AqQeJAyt6BobPIMYko3/cnbmWiVQEsxtsia6TuU2CsLTb1O8ar0ZYny2\n0lg+3nFd1SeRiB+dKw0hy5SpWlznseVgZf3fF6XyKQKBgQDshF0A1ckvtNap8fti\nzXLLS7H1TX/+c8cWLff0FRtMfDqBBn5tv8gVvkxTnPUzD3Ct96EQOETmYJEufkqH\n/hfI3jYprEAkJ0gWH7J5+yZ+EXtc/K42bjKGCND0cQUHZTgtJEus3tcPExLoM8n+\nAuGIIZuG+/0qvVkonr53jTdwpwKBgQDQSeK5QAkHGZlfYdKwnxL2BKuUJn0xmUHw\nEtED+3JHC2wy3r/Y6LeopdoCFKDtab0cLs5GtUfnjCkDU7BEjshFbgJXYkQvnnUy\npgyfR8WlTDaM8+ISE/8r4P/yq4lACZMIkqdKarBGj66KBiy9aZwZ25+82nZD4Qko\nmHRKfi2/mQKBgGofohNj2ZfcTo2GlENq590sI7drhMjJbkUXbzBH4C3bd+y42zWn\nXcHT1y+VN7gnb2m/uLcsaE3uenYgGJUYf9eTTT45mbYfIgs7QbvV4xmiAnZgslKd\n83GMtyVXKOh+lEw9Au+YNWsAJfWmdzXQWR3Z5o0UuC3bNAwz3kaKSJv1AoGAO8jp\nXdjmfnY3kqwmaHHQZHMkuIpvptvhlEIiYm06+O9raBKNqHnrtWmdcLlxE5QlJsC8\njokcEXcmkoDj+FmvXFZeL6zR+4UVCKumtdVJAtAkXELoYd4BgRu8+2+HHq1g2bYW\ndIK5BBfbtlxdXSTCHJ3wdKmUBpnCIjfYMUWUZgkCgYBPFkBKo+RBpq9vJYaQdr0q\nLqfFMiW0GfOb41E7GIsslCRfeBBBM/b9W7aimTskR60VhyypSpdVE3SChDZIPFZC\nt9MUM93bxzuJftpZ5RgyAOFXaPXUAae6fDBJ7wVWQQPru12Kxr8zUa4f6+tFLE3N\nfIHlYv0lcg1C3S6eHCWzTw==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@finance-tracker-nik.iam.gserviceaccount.com",
  "client_id": "115678921324816659986",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40finance-tracker-nik.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


# Check if Firebase app is already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase. Please ensure your firebase_config is correct. Details: {e}")
        st.stop() # Stop the app if initialization fails

db = firestore.client()
# End of Firebase Setup

def get_current_user_id():
    """Returns the current user's ID from session state."""
    return st.session_state.get('user_id')

# --- Authentication Functions ---
def login_page():
    """Displays the login and signup page."""
    st.title("Welcome to Personal Finance Tracker")
    st.markdown("Please log in or create an account to continue.")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                user = auth.get_user_by_email(email)
                # Password validation is handled by Firebase SDK, but for a simplified example
                # we will assume the password is correct after finding the user.
                # A proper Streamlit implementation would use a more robust login flow.
                st.session_state['user_id'] = user.uid
                st.session_state['logged_in'] = True
                st.rerun()
            except exceptions.FirebaseError as e:
                st.error(f"Login failed: {e}")
            except ValueError:
                st.error("Invalid email or password.")
            except Exception:
                st.error("Invalid email or password.")

    with tab2:
        st.subheader("Sign Up")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            try:
                user = auth.create_user(email=signup_email, password=signup_password)
                st.success("Account created successfully! Please log in.")
            except exceptions.FirebaseError as e:
                st.error(f"Sign up failed: {e}")
            except ValueError as e:
                st.error(f"Sign up failed: {e}")


# --- Firestore Functions ---
def add_transaction(user_id, transaction_date, description, amount, category):
    """Inserts a new transaction into the user's Firestore collection."""
    doc_ref = db.collection('users').document(user_id).collection('transactions').document()
    doc_ref.set({
        'date': str(transaction_date),
        'description': description,
        'amount': amount,
        'category': category
    })

def get_transactions_df(user_id):
    """Fetches all transactions for a user from Firestore and returns them as a DataFrame."""
    docs = db.collection('users').document(user_id).collection('transactions').stream()
    data = [doc.to_dict() for doc in docs]
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def add_lending_loan(user_id, lending_date, person, amount, loan_type):
    """Inserts a new lending or loan record for a user into Firestore."""
    doc_ref = db.collection('users').document(user_id).collection('lending_loan').document()
    doc_ref.set({
        'date': str(lending_date),
        'person': person,
        'amount': amount,
        'type': loan_type
    })

def get_lending_loan_df(user_id):
    """Fetches all lending/loan records for a user and returns them as a DataFrame."""
    docs = db.collection('users').document(user_id).collection('lending_loan').stream()
    data = [doc.to_dict() for doc in docs]
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

# --- Keyword-based Categorization ---
def suggest_category(description):
    """Suggests a category based on keywords in the description."""
    keywords = {
        "Food": ["restaurant", "cafe", "groceries", "supermarket", "food", "eat"],
        "Transport": ["gas", "fuel", "bus", "train", "uber", "cab"],
        "Shopping": ["store", "online", "amazon", "mall", "clothes"],
        "Bills": ["rent", "utility", "phone bill", "electricity"],
        "Entertainment": ["movie", "cinema", "concert", "game"],
        "Trip": ["flight", "hotel", "travel", "vacation"],
        "Education/Fees": ["fees", "tuition", "school", "college", "university"],
        "Services": ["service", "repair", "instrument", "maintenance", "repare", "charge"]
    }
    desc = description.lower()
    for category, terms in keywords.items():
        if any(term in desc for term in terms):
            return category
    return "Other"

# --- Main App Dashboard ---
def main_app(user_id):
    """Main dashboard for the finance tracker."""
    # Custom CSS for the sky blue and pink gradient background
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(to right, #87CEEB, #FFC0CB);
        }}
        .stTabs [data-baseweb="tab-list"] button {{
            font-size: 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    transactions_df = get_transactions_df(user_id)
    lending_df = get_lending_loan_df(user_id)

    # --- Top Row: Title and Summary ---
    title_col, summary_col = st.columns([1, 1])
    with title_col:
        st.title("💰 Personal Finance Tracker")
    with summary_col:
        st.subheader("📊 Overall Summary")
        
        total_expenses = transactions_df['amount'].sum() if not transactions_df.empty else 0
        total_lent = lending_df[lending_df['type'] == 'Lent']['amount'].sum() if not lending_df.empty else 0
        total_loan = lending_df[lending_df['type'] == 'Loan']['amount'].sum() if not lending_df.empty else 0
        
        st.markdown(f"**Overall Expenses:** ₹{total_expenses:,.2f}")
        st.markdown(f"**Overall Money Lent:** ₹{total_lent:,.2f}")
        st.markdown(f"**Overall Money Taken as Loan:** ₹{total_loan:,.2f}")
        
    st.markdown("---")
    
    # --- Second Row: Add Transaction and Expense Trends (All in one row) ---
    st.subheader("➕ Add New Transaction & 📈 Expense Trends")
    trans_col, daily_col, weekly_col, monthly_col = st.columns(4)
    
    with trans_col:
        with st.form("transaction_form", clear_on_submit=True):
            transaction_date = st.date_input("Date", value=date.today())
            description = st.text_input("Description")
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")

            # Updated list of categories
            categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Trip", "Education/Fees", "Services", "Other"]
            
            suggested_cat = suggest_category(description)
            category = st.selectbox("Category", options=categories, index=categories.index(suggested_cat))

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                if description and amount:
                    add_transaction(user_id, str(transaction_date), description, amount, category)
                    st.success("Transaction added successfully!")
                else:
                    st.error("Please fill in the description and amount.")
    
    if not transactions_df.empty:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        transactions_df['week'] = transactions_df['date'].dt.to_period('W').astype(str)
        transactions_df['month'] = transactions_df['date'].dt.to_period('M').astype(str)
        
        with daily_col:
            daily_expenses = transactions_df.groupby(transactions_df['date'].dt.date)['amount'].sum().reset_index()
            fig_daily = px.bar(daily_expenses, x='date', y='amount', title='Daily Expenses')
            st.plotly_chart(fig_daily, use_container_width=True, config={'staticPlot': True})

        with weekly_col:
            weekly_expenses = transactions_df.groupby('week')['amount'].sum().reset_index()
            fig_weekly = px.bar(weekly_expenses, x='week', y='amount', title='Weekly Expenses')
            st.plotly_chart(fig_weekly, use_container_width=True, config={'staticPlot': True})
        
        with monthly_col:
            monthly_expenses = transactions_df.groupby('month')['amount'].sum().reset_index()
            fig_monthly = px.bar(monthly_expenses, x='month', y='amount', title='Monthly Expenses')
            st.plotly_chart(fig_monthly, use_container_width=True, config={'staticPlot': True})
    else:
        # Fallback for empty transactions data
        with daily_col:
            st.info("No transactions to show trends.")
            
    st.markdown("---")

    # --- Third Row: Money Lending & Loans ---
    lending_form_col, lending_chart_col = st.columns([1, 1])
    with lending_form_col:
        st.subheader("🤝 Money Lending & Loans")
        with st.form("lending_loan_form", clear_on_submit=True):
            lending_date = st.date_input("Date of transaction", value=date.today())
            person = st.text_input("Person's Name")
            loan_amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            loan_type = st.radio("Type", ("Lent", "Loan"))
            loan_submitted = st.form_submit_button("Add Record")

            if loan_submitted:
                if person and loan_amount:
                    add_lending_loan(user_id, str(lending_date), person, loan_amount, loan_type)
                    st.success("Record added successfully!")
                else:
                    st.error("Please fill in the person's name and amount.")

    with lending_chart_col:
        lending_df = get_lending_loan_df(user_id)
        if not lending_df.empty:
            st.subheader("Bar Chart of Money Lent vs. Loans Taken")
            lending_df['date'] = pd.to_datetime(lending_df['date'])
            lending_df['month'] = lending_df['date'].dt.to_period('M').astype(str)
            monthly_lending_loan = lending_df.groupby(['month', 'type'])['amount'].sum().reset_index()
            fig_lending = px.bar(monthly_lending_loan, x='month', y='amount', color='type', title='Monthly Money Lent vs. Loans', barmode='group')
            st.plotly_chart(fig_lending, use_container_width=True, config={'staticPlot': True})
        else:
            st.info("No lending or loan records to display.")
    
    st.markdown("---")
    
    # --- Fourth Row: Good vs. Bad Expenses ---
    goodbad_text_col, goodbad_chart_col = st.columns([1, 1])
    with goodbad_text_col:
        st.subheader("🤔 Good vs. Bad Expenses")
        bad_categories = ["Entertainment", "Food", "Trip"]
        
        # Ensure transactions_df is not empty before filtering
        if not transactions_df.empty:
            bad_expenses_df = transactions_df[transactions_df['category'].isin(bad_categories)]
            total_bad_expenses = bad_expenses_df['amount'].sum()
        else:
            bad_expenses_df = pd.DataFrame()
            total_bad_expenses = 0
            
        st.markdown(f"**Total amount you could have saved:** ₹{total_bad_expenses:,.2f}")
        
        st.subheader("💡 Suggestions")
        st.info(f"You could save approximately **₹{total_bad_expenses:,.2f}** next month by controlling your spending on entertainment, food, and trips.")
        
    with goodbad_chart_col:
        st.subheader("Bar Chart of Good and Bad Expenses")
        if not transactions_df.empty:
            good_expenses_df = transactions_df[~transactions_df['category'].isin(bad_categories)]
            
            weekly_bad = bad_expenses_df.groupby('week')['amount'].sum().reset_index()
            weekly_good = good_expenses_df.groupby('week')['amount'].sum().reset_index()
            weekly_combined = pd.merge(weekly_bad, weekly_good, on='week', how='outer', suffixes=('_bad', '_good')).fillna(0)
            weekly_combined = weekly_combined.melt(id_vars='week', value_vars=['amount_bad', 'amount_good'], var_name='type', value_name='amount')
            weekly_combined['type'] = weekly_combined['type'].replace({'amount_bad': 'Bad Expenses', 'amount_good': 'Good Expenses'})
            fig_weekly_goodbad = px.bar(weekly_combined, x='week', y='amount', color='type', title='Weekly Good vs Bad Expenses', barmode='group')
            st.plotly_chart(fig_weekly_goodbad, use_container_width=True, config={'staticPlot': True})

            monthly_bad = bad_expenses_df.groupby('month')['amount'].sum().reset_index()
            monthly_good = good_expenses_df.groupby('month')['amount'].sum().reset_index()
            monthly_combined = pd.merge(monthly_bad, monthly_good, on='month', how='outer', suffixes=('_bad', '_good')).fillna(0)
            monthly_combined = monthly_combined.melt(id_vars='month', value_vars=['amount_bad', 'amount_good'], var_name='type', value_name='amount')
            monthly_combined['type'] = monthly_combined['type'].replace({'amount_bad': 'Bad Expenses', 'amount_good': 'Good Expenses'})
            fig_monthly_goodbad = px.bar(monthly_combined, x='month', y='amount', color='type', title='Monthly Good vs Bad Expenses', barmode='group')
            st.plotly_chart(fig_monthly_goodbad, use_container_width=True, config={'staticPlot': True})
        else:
            st.info("No expense data to analyze.")

    st.markdown("---")

    # --- Display All Transactions and Lending/Loan Records at the bottom ---
    st.subheader("All Records")
    tab1, tab2 = st.tabs(["🧾 Transactions", "🤝 Lending/Loans"])
    with tab1:
        if not transactions_df.empty:
            st.dataframe(transactions_df, use_container_width=True)
        else:
            st.info("No transactions recorded yet.")

    with tab2:
        if not lending_df.empty:
            st.dataframe(lending_df, use_container_width=True)
        else:
            st.info("No lending or loan records yet.")


def app():
    """Main application loop that manages user sessions."""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None

    if st.session_state['logged_in']:
        main_app(st.session_state['user_id'])
    else:
        login_page()

if __name__ == "__main__":
    app()
