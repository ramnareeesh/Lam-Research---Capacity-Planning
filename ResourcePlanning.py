import streamlit as st
import pulp
import pandas as pd
import json


def app():

    st.title("CAPACITY PLANNING MODULE")
    st.header("Resource Planning")


    st.write("---")

    option = st.radio(label="Choose input style", options=["Config file upload", "UI Input"])

    st.write("---")

    if option == "Config file upload":
        config_file = st.file_uploader(label="Upload file here", type=["json"])
        if config_file is not None:
            params = json.load(config_file)
            config = st.selectbox("Select a configuration", list(params.keys()))
            params = params[config]
            days = params["days"]
            predicted_demand_arr = params["predicted_demand"]
            worker_cost = params["worker_cost"]
            supply_cost = params["supply_cost"]
            lowerBound_workers = params["lowerBound_workers"]
            lowerBound_supplies = params["lowerBound_supplies"]
            proportion = params["proportion"]
            max_change_workers = params["max_change_workers"]
            max_change_supplies = params["max_change_supplies"]
            st.subheader("Configurations")
            st.write(f"Days: {days}")
            st.write(f"Predicted Demand: {predicted_demand_arr}")
            st.write(f"Worker Cost: {worker_cost}")
            st.write(f"Supply Cost: {supply_cost}")
            st.write(f"Lower Bound Workers: {lowerBound_workers}")
            st.write(f"Lower Bound Supplies: {lowerBound_supplies}")
            st.write(f"Proportion: {proportion}")
            st.write(f"Max Change Workers: {max_change_workers}")
            st.write(f"Max Change Supplies: {max_change_supplies}")

    if option == "UI Input":
        st.subheader("Bounds")

        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                days = st.number_input("No. of days", step=1, format="%d", min_value=0)
                predicted_demand = st.text_input("Predicted Demand", placeholder="space separated")

            with col2:
                worker_cost = st.number_input("Cost per worker", step=0.5, format="%f", min_value=1.0)
                supply_cost = st.number_input("Cost per supply", step=0.5, format="%f", min_value=1.0)

        if predicted_demand:
            predicted_demand_arr = list(map(int, predicted_demand.strip(" ").split(" ")))

            if len(predicted_demand_arr) != days:
                st.error("Error: entered demand values don't match with no. of days")

        col1, col2 = st.columns(2)
        with col1:
            lowerBound_workers = st.number_input("Workers: Lower Bound", step=1, format="%d", min_value=1)

        with col2:
            lowerBound_supplies = st.number_input("Supplies: Lower Bound", step=1, format="%d", min_value=1)

        st.write("---")
        st.subheader("Constraints")
        proportion = st.slider("Proportionality Constraint: no. of units of supplies required per worker", value=None, max_value=10)

        col1, col2 = st.columns(2)
        with col1:
            max_change_workers = st.number_input("Maximum change in no. of workers", step=1, format="%d", min_value=0)

        with col2:
            max_change_supplies = st.number_input("Maximum change in no. of supplies", step=1, format="%d", min_value=0)

    if st.button("Run!"):

        st.write("---")

        prob = pulp.LpProblem("ResourcePlanning", pulp.LpMinimize)
        workers = [pulp.LpVariable(f"workers_day_{i}", lowBound=lowerBound_workers, cat='Integer') for i in range(days)]
        supplies = [pulp.LpVariable(f"supplies_day_{i}", lowBound=lowerBound_supplies, cat='Integer') for i in range(days)]

        prob += pulp.lpSum([worker_cost * workers[i] + supply_cost * supplies[i] for i in range(days)])

        for i in range(days):
            prob += workers[i] * proportion + supplies[i] >= predicted_demand_arr[i]

        for i in range(1, days):
            prob += workers[i] - workers[i-1] <= max_change_workers
            prob += supplies[i] - supplies[i-1] <= max_change_supplies
            prob += workers[i-1] - workers[i] <= max_change_workers
            prob += supplies[i-1] - supplies[i] <= max_change_supplies

        for i in range(days):
            prob += supplies[i] >= proportion * workers[i], f"ProportionalConstraint_day_{i}"


        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        st.subheader("Optimized Workers and Supplies")
        opt_workers = []
        opt_supplies = []
        for i in range(days):

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label=f"Day {i + 1}", value=f"Day {i + 1}", label_visibility="hidden")
            with col2:
                st.metric(label="**Workers**", value=pulp.value(workers[i]))
            with col3:
                st.metric(label="**Supplies**", value=pulp.value(supplies[i]))
            opt_workers.append(pulp.value(workers[i]))
            opt_supplies.append(pulp.value(supplies[i]))


        data = {
            'Days': range(1, days + 1),
            'Demand': predicted_demand_arr,
            'Workers': opt_workers,
            'Supplies': opt_supplies
        }
        df = pd.DataFrame(data)

        st.write("\n\n")

        st.dataframe(df, hide_index=True, use_container_width=True)

        df.set_index('Days', inplace=True)

        st.write("---")
        st.subheader("Visualization")
        st.line_chart(df)
        st.bar_chart(df)
        st.area_chart(df)

        st.write("---")
app()