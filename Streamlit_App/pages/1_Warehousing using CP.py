import streamlit as st
import matplotlib.pyplot as plt
from pulp import *
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("CAPACITY PLANNING MODULE")
st.header("Warehousing using Constraint Programming")
st.write("---")
st.subheader("Warehouses [Supply]")

warehouse_count = st.number_input("No. of Warehouses", step=1, format="%d", min_value=1)
supply = {}
for i in range(warehouse_count):
    st.write(f"**--- Warehouse {i+1} ---**")
    warehouse_capacity = st.number_input(
        f"Warehouse {i+1} Capacity", step=1, format="%d", min_value=1
    )
    st.write("\n")
    st.write("\n")

    supply[f"Warehouse {i+1}"] = warehouse_capacity

warehouses = list(supply.keys())


st.write("---")

st.subheader("Customers [Demand]")
customer_count = st.number_input("No. of Customers", step=1, format="%d", min_value=1)
demand = {}
for i in range(customer_count):
    st.write(f"**--- Customer {i+1} ---**")
    customer_demand = st.number_input(
        f"Customer {i+1} Demand", step=1, format="%d", min_value=1
    )
    st.write("\n")
    st.write("\n")

    demand[f"Customer {i+1}"] = customer_demand

customers = list(demand.keys())


st.write("---")

st.subheader("Costs")
costs = []
for warehouse in warehouses:
    warehouse_cost = []
    for customer in customers:
        cost = st.number_input(
            f"Cost of {warehouse} to {customer}", step=1, format="%d", min_value=1
        )
        st.write("\n")
        st.write("\n")
        warehouse_cost.append(cost)
    costs.append(warehouse_cost)

cost_dict = makeDict([warehouses, customers], costs, 0)


prob = LpProblem("WarehousingPlanning", LpMinimize)
Routes = [(w, c) for w in warehouses for c in customers]
vars = LpVariable.dicts("Route", (warehouses, customers), 0, None, LpInteger)


prob += (
    lpSum([vars[w][c] * cost_dict[w][c] for (w, c) in Routes]),
    "Sum of Transporting Costs",
)
for w in warehouses:
    prob += (
        lpSum([vars[w][c] for c in customers]) <= supply[w],
        f"Sum of Products from Warehouse {w}",
    )

for c in customers:
    prob += (
        lpSum([vars[w][c] for w in warehouses]) >= demand[c],
        f"Sum of Products to Customer {c}",
    )


def generate_LP_file():
    prob.writeLP("WarehousingPlanning.lp")


st.button("Generate LP file", on_click=generate_LP_file)


# prob.solve(pulp.PULP_CBC_CMD(msg=False))
# st.write(pulp.value(vars[warehouse[0]][customer[0]]))
# for v in prob.variables():
#     st.write(v.name, "=", v.varValue)


# Deva's function to create graph using PyVis
def create_graph(net):

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = "/tmp"
        net.save_graph(f"{path}/pyvis_graph.html")
        HtmlFile = open(f"{path}/pyvis_graph.html", "r", encoding="utf-8")

    # Save and read graph as HTML file (locally)
    except:
        net.show("pyvis_graph.html")
        HtmlFile = open("pyvis_graph.html", "r", encoding="utf-8")

    # Read the HTML file
    source_code = HtmlFile.read()

    # custom_html = f"""
    # <div style="border-bottom:2px solid #000;">
    #     {source_code}
    # </div>
    # """

    return components.html(source_code, height=750)


st.write("---")
if st.button("Run!"):
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    for w in warehouses:
        st.subheader(f"{w}")

        st.dataframe(
            pd.DataFrame(
                [[c, vars[w][c].varValue] for c in customers],
                columns=["Customer", "No. of Units"],
            ),
            hide_index=True,
            use_container_width=True,
        )

    solution = {i.name: i.varValue for i in prob.variables()}

    G = Network(
        height="500px",
        width="100%",
        bgcolor="white",
        font_color="black",
        directed=True,
        neighborhood_highlight=True,
        cdn_resources="remote",
    )

    for w in warehouses:
        G.add_node(w, label=w, title=str(w), group=0, color="blue")

    for c in customers:
        G.add_node(c, label=c, title=str(c), group=1, color="navy")

    for w in warehouses:
        for c in customers:
            if vars[w][c].varValue > 0:
                G.add_edge(
                    w, c, weight=vars[w][c].varValue, title=str(vars[w][c].varValue)
                )

    st.header("Graph Visualization")
    create_graph(G)
