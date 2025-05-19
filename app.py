import streamlit as st
import pandas as pd
import openai

st.title("🗺️ Final Mile AI Planner")

uploaded_file = st.file_uploader("Upload your delivery data CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📦 Delivery Data", df)

    constraints = st.text_area("Constraints", 
        "Max 5 deliveries per route\nPrioritize 'High' priority deliveries first\nStay within time windows")

    if st.button("Generate Route Plan with GenAI"):
        prompt = f"""You are a logistics route planner. Based on the delivery data and constraints below, suggest an efficient route and explain why.

Constraints:
{constraints}

Delivery Data:
{df.to_csv(index=False)}
"""

        openai.api_key = st.secrets["OPENAI_API_KEY"]  # Add your API key in .streamlit/secrets.toml

        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        st.write(response.choices[0].message.content)

        st.subheader("🧠 AI-Suggested Route Plan")
        st.write(response.choices[0].message.content)

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import numpy as np

# Distance matrix mockup (10x10, symmetric) for demonstration
def create_distance_matrix(num_deliveries):
    np.random.seed(1)
    matrix = np.random.randint(5, 50, size=(num_deliveries, num_deliveries))
    np.fill_diagonal(matrix, 0)
    return matrix.tolist()

def optimize_route(distance_matrix):
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        return route
    return None

