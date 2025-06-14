
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Transport Route Optimizer", page_icon="🚛")

st.title("🧬 Transport Route Optimizer (GA Based)")

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=None)
    st.success("✅ Excel file loaded successfully!")

    if 'Demand' in df and 'Cost' in df:
        demand_df = df['Demand']
        cost_df = df['Cost']
        
        st.subheader("📈 Demand Data")
        st.write(demand_df)

        st.subheader("💰 Cost Data")
        st.write(cost_df)

        st.subheader("⚙️ Optimization Parameters")
        pop_size = st.slider("Population Size", 10, 100, 20)
        generations = st.slider("Number of Generations", 10, 100, 30)
        mutation_rate = st.slider("Mutation Rate (%)", 0, 100, 5) / 100

        if st.button("🚀 Run Optimization"):
            routes = list(zip(demand_df['From'], demand_df['To']))
            demand = demand_df['Demand'].tolist()
            company_costs = cost_df['Company'].tolist()
            third_party_costs = cost_df['3PL'].tolist()

            def fitness(individual):
                total_cost = 0
                for i, gene in enumerate(individual):
                    total_cost += (company_costs[i] if gene == 0 else third_party_costs[i]) * demand[i]
                return -total_cost  # minimize cost

            def mutate(individual):
                idx = random.randint(0, len(individual) - 1)
                individual[idx] = 1 - individual[idx]
                return individual

            def crossover(parent1, parent2):
                point = random.randint(1, len(parent1) - 1)
                return parent1[:point] + parent2[point:]

            # Initialize population
            population = [[random.randint(0, 1) for _ in routes] for _ in range(pop_size)]

            for gen in range(generations):
                population = sorted(population, key=fitness)
                new_population = population[:2]  # Elitism

                while len(new_population) < pop_size:
                    p1, p2 = random.choices(population[:10], k=2)
                    child = crossover(p1, p2)
                    if random.random() < mutation_rate:
                        child = mutate(child)
                    new_population.append(child)

                population = new_population

            best_solution = population[0]
            total_cost = -fitness(best_solution)

            result_df = demand_df.copy()
            result_df['Decision'] = ['Company' if x == 0 else '3PL' for x in best_solution]
            result_df['Unit Cost'] = [company_costs[i] if x == 0 else third_party_costs[i] for i, x in enumerate(best_solution)]
            result_df['Total Route Cost'] = [c * d for c, d in zip(result_df['Unit Cost'], demand)]

            st.success(f"✅ Optimization Completed. Total Cost: SAR {total_cost:,.2f}")
            st.dataframe(result_df)
    else:
        st.error("❌ Please make sure the Excel file includes 'Demand' and 'Cost' sheets.")
else:
    st.warning("📎 Please upload an Excel file to begin.")
