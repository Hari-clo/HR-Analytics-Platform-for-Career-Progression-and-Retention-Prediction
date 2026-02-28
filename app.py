import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config("Career Intelligence System", layout="wide")

@st.cache_data
def load():
    d = pd.read_csv("data/final_career_intelligence.csv")
    d["PromotionRiskScore"] = (
        d["PromotionGapRatio"]*50 +
        d["RoleStagnationIndex"]*30 +
        (1-d["TrainingIntensityScore"].clip(0,1))*20
    ).clip(0,100).round(1)
    return d

d = load()

st.title("Enterprise Career Progression Intelligence System")

dept = ["All"] + sorted(d["Department"].unique())
dept_sel = st.radio("Select Department", dept, horizontal=True)

risk_sel = st.sidebar.multiselect(
    "Promotion Risk",
    d["PromotionGapRisk"].unique(),
    d["PromotionGapRisk"].unique()
)

cluster_sel = st.sidebar.multiselect(
    "Career Cluster",
    d["CareerClusterLabel"].unique(),
    d["CareerClusterLabel"].unique()
)

f = d.copy()
if dept_sel != "All":
    f = f[f["Department"] == dept_sel]

f = f[
    (f["PromotionGapRisk"].isin(risk_sel)) &
    (f["CareerClusterLabel"].isin(cluster_sel))
]

total = len(f)
high = len(f[f["PromotionGapRisk"]=="High"])
priority = len(f[f["RetentionOpportunityIndex"]==3])
avg = round(f["PromotionRiskScore"].mean(),1)

c1,c2,c3,c4 = st.columns(4)
c1.metric("Employees", total)
c2.metric("High Risk", high)
c3.metric("Retention Priority", priority)
c4.metric("Avg Risk Score", avg)

if priority:
    st.warning(f"{priority} employees need career intervention.")
else:
    st.success("Career progression appears healthy.")

col1,col2 = st.columns(2)

with col1:
    st.subheader("Career Clusters")
    st.plotly_chart(
        px.pie(f, names="CareerClusterLabel", hole=0.5),
        width="stretch"
    )

with col2:
    st.subheader("Promotion Risk Levels")
    rc = f["PromotionGapRisk"].value_counts().reset_index()
    rc.columns=["Risk","Count"]
    st.plotly_chart(
        px.bar(rc, x="Risk", y="Count", color="Risk"),
        width="stretch"
    )

st.subheader("Risk Score Distribution")
st.plotly_chart(
    px.histogram(f, x="PromotionRiskScore", nbins=30),
    width="stretch"
)

st.subheader("Manager Effectiveness")

mgr = f.groupby("YearsWithCurrManager")["PromotionRiskScore"] \
       .mean().reset_index()

st.plotly_chart(
    px.scatter(mgr,
        x="YearsWithCurrManager",
        y="PromotionRiskScore"),
    width="stretch"
)

st.subheader("High Risk Employees")

st.dataframe(
    f[f["PromotionRiskScore"]>70][[
        "Department",
        "JobRole",
        "YearsAtCompany",
        "PromotionRiskScore"
    ]],
    width="stretch"
)