import streamlit as st
import pandas as pd
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title = "Mining Health and Safety System",
    page_icon = "🛡️",
    layout = "wide"
)

# File location
WORKER_FILE = "worker_safety.csv"
INCIDENT_FILE = "safety_incidents.csv"
EQUIPMENT_FILE = "equipment.csv"
MAINTENANCE_FILE = "maintenance.csv"

def load_data(filename):
    """Load a CSV file and show a clear error if it cannot be opened."""
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        st.error(
            f"Could not find {filename}. Put it in the same folder "
            "as your Streamlit Python file."
        )
        return pd.DataFrame()
    except Exception as error:
        st.error(f"Could not read {filename}: (error)")
        return pd.DataFrame()

worker_data = load_data(WORKER_FILE)
incident_data = load_data(INCIDENT_FILE)
equipment_data = load_data(EQUIPMENT_FILE)
maintenance_data = load_data(MAINTENANCE_FILE)

# User accounts

users = {
    "admin":{
        "password": "admin123",
        "role": "Administrator"
    },
    "safety": {
        "password": "safety123",
        "role": "Safety Officer"
    },
    "mining": {
        "password": "mining123",
        "role": "Mining Engineer"
    },
    "maintenance": {
        "password": "maintenance123",
        "role": "Maintenance Engineer"
    },
    "manager": {
        "password": "manager123",
        "role": "Manager"
    }
}

#Permissions for each role

permissions = {
    "Administrator": [
        "Dashboard",
        "Worker Safety", 
        "Safety Incidents", 
        "Maintenance", 
        "Risk Assessment", 
        "Reports", 
        "Manage Users"
    ],
    "Safety Officer":[
        "Dashboard",
        "Worker Safety",
        "Risk Assessment", 
        "Reports", 
        "Safety Incidents",
        "Manage Users"
    ],
    "Mining Engineer": [
        "Dashboard",
        "Worker Safety", 
        "Safety Incidents", 
        "Maintenance", 
        "Risk Assessment", 
        "Reports", 
                
    ],
    "Maintenance Engineer": [
        "Dashboard", 
        "Maintenance", 
        "Reports",
        "Equipment"
    ],
    "Manager":[
        "Dashboard",
        "Worker Safety", 
        "Safety Incidents", 
        "Maintenance", 
        "Risk Assessment", 
        "Reports"
    ]
}

# Find a column without depending on spaces, underscores or capitalisation
def normalise(text):
    return "".join(character.lower() for character in str(text)
                   if character.isalnum())
    
def find_column(data, keywords):
    normalised_columns = {normalise(column): column for column in data.columns}
    normalised_keywords = [normalise(word) for word in keywords]
    
    for column_key, original_column in normalised_columns.items():
        if any(word in column_key for word in normalised_keywords):
            return original_column
    return None

# Styling

st.markdown("""
            <style>
            /* Main background */
            .stApp {
                background-color: #F4F7FB;
                    color: #26374A;
            }
            
            /* Main title and heading */
            h1, h2, h3 {
                color: #263F5B;
            }
            
            /* Sidebar */
            
            [data-setid = "stSidebar"] * {
                color: #FFFFFF;
            }
            
            /* Metric cards */
            [data-testid = "stMetric"] {
                background-color: #FFFFFF;
                    border: 1px solid #DCE5EE;
                    padding: 18px;
            }
            [data-testid = "stMetricLabel"] {
                color: #52677D;
            }
            [data-testid = "stMetricLabel"] {
                color: #52677D;
            }
            [data-testid = "stMetricValue"] {
                color: #304A66;
            }
            
            /* Buttons */
            .stButton > button {
                background-color: #397D86;
                    color: white;
                    border: none;
                    padding: 8px 16px;
            }
            
            .stButton > button:hover {
                background-color: #2C646C;
                    color: white;
            }
            /* Table */
            [data-testid = "stDataFrame"],
            [data-testid = "stDataEditor"] {
                border: 1px solid #DCE5EE;
                border-radius: 8px;
            }
            </style>
            """, unsafe_allow_html = True)


# Login state
if  "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if "role" not in st. session_state:
    st.session_state.role = ""

st.title("Mining Health, Safety and Equipment Monitoring System")
st.caption("Monitoring worker safety, incidents and equipment performance.")

# Login page
if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type= "password")
    
    if st.button("Login"):
        if username in users and users [username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = users[username]["role"]
            st.rerun()
        else:
            st.error("Invalid username or password.")

# Application pages
if st.session_state.logged_in:
    role = st.session_state.role
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Go to:", permissions[role])
    st.sidebar.write("Logged in as: **(role)**")
    
    #Dashboard
    
    if selected_page == "Dashboard":
        st.subheader("Operations Dashboard")
        st.write(
            "An overview of worker safety,recorded incidents, "
            "equipment and maintenance."
        )
    
        # Four summary cards 
        total_workers = len(worker_data)
        total_incidents = len(incident_data)
        total_equipment = len(equipment_data)
        total_maintenance = len(maintenance_data)
        
        col1, col2, col3, col4 = st.columns(4)   
        col1.metric("Worker Records", total_workers)
        col2.metric("Safety Incidents", total_incidents)
        col3.metric("Equipment Records", total_equipment)
        col4.metric("Maintenance Records", total_maintenance)
                    
        st.divider()
        st.subheader("Worker Safety Overview")
        
        ppe_column = find_column(
                worker_data,
                ["ppe compliance", "ppe"]
            )
        training_column = find_column(
                worker_data,
                ["safety training status", "training status"]
            )
        left, right =st.columns(2)
        
        # PPE metric
        with left:
            if ppe_column is not None and not worker_data.empty:
                ppe_values = (
                    worker_data[ppe_column]
                    .astype(str).str.strip().str.lower()
                )
                valid_ppe = ppe_values.isin(["yes", "no"])
                
                if valid_ppe.any():
                    ppe_percentage = (
                        ppe_values[valid_ppe].eq("yes").mean()*100
                    )
                    st.metric("PPE Compliance", f"{ppe_percentage:1f}%")
                else:
                    st.info(
                        "PPE column found, but it has no YES/NO values "
                        "to calculate compliance."
                    )
            else:
                st.info(
                    "PPE column not found. Check the column names "
                    "in worker_safety.csv."
                )
        # Training metric
        with right:
            if training_column is not None and not worker_data.empty:
                training_values = (
                    worker_data[training_column]
                    .astype(str).str.strip().str.lower()
                )
                incomplete = training_values.isin(
                    ["incomplete", "no", "not complete"]
                ).sum()               
                st.metric("Incomplete Training Records", int(incomplete))
            else:
                st.info(
                    "Training status column not found.Check "
                    "worker_safety.csv."
                )
        st.divider()
        st.subheader("Safety Incidents Department")
                            
        department_column = find_column(incident_data, ["department"])
        
        if department_column is not None and not incident_data.empty:
            department_counts = (
                incident_data[department_column]
                .dropna()
                .astype(str)
                .str.strip()
                .value_counts()
                .rename_axis("Department")
                .reset_index(name= "Number of Incidents")
            )
            
            if not department_counts.empty:
                st.bar_chart(
                    department_counts.set_index("Department")
                )
            else:
                st.info("No department values are available to chart.")
        else:
            st.info(
                "The incidents dataset has no department column, "
                "so this graph cannot be generated."
            )
                
        st.divider()
        st.subheader("Safety Alerts")
        alerts_found = False
        
        if ppe_column is not None and not worker_data.empty:
            ppe_values = (
                worker_data[ppe_column]
                .astype(str).str.strip().str.lower()
            )
            ppe_issues = int(ppe_values.eq("no").sum())
            
            if ppe_issues > 0:
                st.warning(
                    f"{ppe_issues} worker record(s) indicate PPE "
                    "non-compliance. Follow up with the safety officer."
                )
                alerts_found = True
                
        if training_column is not None and not worker_data.empty:
            training_values = (
                worker_data[training_column]
                .astype(str).str.strip().str.lower()
            )
            training_issues = int(
                training_values.isin(
                    ["incomplete", "no", "not complete"]
                ).sum()
            )
            
            if training_issues > 0:
                st.warning(
                    f"{training_issues} worker record(s) indicate "
                    "incomplete safety training."
                )
                alerts_found = True
                
        if not alerts_found:
            st.success(
                "No PPE or incomplete-training issues were detected "
                "in the available records. This does not confirm that "
                "the mine is hazard-free."
            )
            
        st.caption("Dashboard results are based on the current CSV records")
        
    # Worker safety
    
    if selected_page == "Worker Safety":
        st.subheader("Worker Safety Monitoring")
        
        edited_worker_data = st.data_editor(
            worker_data,
            num_rows = "dynamic",
            use_container_width = True
        )
        
        if st.button("Save Worker Safety Changes"):
            edited_worker_data.to_csv(
                "worker_safety.csv",
                index = False
            )
            
            st.success(
                "Worker safety changes saved successfully!"
            )
            
    # Safetyn Incidents
    
    if selected_page == "Safety Incidents":
        st.subheader("Safety Incidents Database")
        st.write("Edit the safety incident records below.")
        
        edited_incident_data = st.data_editor(
            incident_data,
            num_rows = "dynamic", 
            use_container_width = True
        )
        if st.button("Save Safety Incident Change"):
            edited_incident_data.to_csv(
                "safety_incidents.csv",
                index = False
            )
            incident_data = edited_incident_data.copy()
        
            st.success(
            "Safety incident changes saved successfully!"
            )
        
    #Equipment
    
    if selected_page == "Equipment":
        st.subheader("Equipment Monitoring")
        st.write("Edit the equipment records below.")
        edited_equipment_data = st.data_editor(
            equipment_data,
            num_rows ="dynamic",
            use_container_width = True
        )
        
        if st.button("Save Equipment Changes"):
            edited_equipment_data.to_csv(
                EQUIPMENT_FILE,
                index = False
            )
            equipment_data = edited_equipment_data.copy()
            st.success(
                "Equipment changes saved successfully!"
            )
    
    #Maintenance
        
    if selected_page == "Maintenance":
        st.subheader("Equipment Maintenance")
        st.write("Edit the maintenance records below.")
        edited_maintenance_data = st.data_editor(
            maintenance_data,
            num_rows = "dynamic",
            use_container_width=True
        )
        if st.button("Save Maintenance changes"):
            edited_maintenance_data.to_csv(
                MAINTENANCE_FILE,
                index = False
            )
            maintenance_data = edited_maintenance_data.copy()
            
            st.success("Maintenance changes saved successfully!")
    
    # Risk Assessment
    
    if selected_page == "Risk Assessment" :
        st.subheader("Worker Risk Assessment")
        
        risk_column = find_column(worker_data, ["risk level"])
        fatigue_column = find_column(worker_data, ["fatique level"])
        ppe_column = find_column(worker_data, ["ppe compliance", "ppe"])
        training_column = find_column(
            worker_data, ["safety training status", "training status"]
        )
        
        if worker_data.empty:
            st.info("No worker records are available.")
        else:
            risk_found = False
            
            if risk_column is not None:
                st.write("Records by recorded risk level")
                st.bar_chart(worker_data[risk_column].value_counts())
                risk_found = True
            
            if fatigue_column is not None:
                try:
                    high_fatigue = (
                        pd.to_numeric(worker_data[fatigue_column],
                                      errors="coerce") >= 4
                    ).sum()
                    st.metric("Workers with Fatigue Level 4 or 5",
                              int(high_fatigue))
                    risk_found = True
                except Exception:
                    pass
                
            if ppe_column is not None:
                ppe_values = (
                    worker_data[ppe_column].astype(str).str.strip().str.lower()
                )
                st.metric("PPE Non-compliance Records",
                          int(ppe_values.eq("no").sum()))
                risk_found = True
            
            if training_column is not None:
                training_values = (
                    worker_data[training_column]
                    .astype(str).str.strip().str.lower()
                )
                st.metric(
                    "Incomplete Training Records",
                    int(training_values.isin(["incomplete", "no", "not complete"]).sum())
                )
                risk_found = True
            
            if not risk_found:
                st.info("No recognised risk columns were found in the dataset")
            
            st.caption(
                "These indicators support review; they do not replace"
                "a formal workplace risk assessment."
            )
            
    # Reports
    
    if selected_page == "Reports":
        st.subheader("Mining Safety and Equipment Reports")
        st.write("Summary of the records currently available.")
        
        report1, report2, report3, report4 = st.columns(4)
        report1.metric("Worker Records", len(worker_data))
        report2.metric("Safety Incidents", len(incident_data))
        report3.metric("Equipment Records", len(equipment_data))
        report4.metric("Maintenance Records", len(maintenance_data))
        
        st.subheader("Download Data")
        download1, download2 = st.columns(2)
        
        with download1:
            st.download_button(
                "Download Worker Safety CSV",
                data = worker_data.to_csv(index=False).encode("utf-8"),
                file_name = "worker_safety_report.csv",
                mime="text/csv"
            )
            st.download_button(
                "Download Safety Incidents CSV",
                data = incident_data.to_csv(index=False).encode("utf-8"),
                file_name="safety_incidents_report.csv",
                mime="text/csv"
            )
            
        with download2:
            st.download_button(
                "Download Equipment CSV",
                data=equipment_data.to_csv(index=False).encode("utf-8"),
                file_name="equipment_report.csv",
                mime="text/csv"
            )
            st.download_button(
                "Download Maintenance CSV",
                data=maintenance_data.to_csv(index=False).encode("utf-8"),
                file_name="maintenance_report.csv",
                mime="text/csv"
            )
    
    # Manage users
    
    if selected_page == "Manage Users":
        if role != "Administrator":
            st.error("Only the Administrator can manage users.")
        else:
            st.subheader("Manage Users")
            user_summary = pd.DataFrame([
                {"Username": name, "Role": details["role"]}
                for name, details in users.items()
            ])
            st.dataframe(user_summary, use_container_width=True)
            st.caption(
                "This demostration lists accounts only. It does not "
                "create users or change passwords."
            )
    #Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False 
        st.session_state.role =""
        st.rerun()
    
    
