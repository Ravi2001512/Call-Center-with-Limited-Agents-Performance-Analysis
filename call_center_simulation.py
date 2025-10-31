import simpy
import random
import statistics
import csv
import os

# Simulation Parameters
RANDOM_SEED = 42
ARRIVAL_RATE = 30 / 60   # 30 calls per hour (calls/minute)
MEAN_SERVICE = 6         # average service time in minutes
SIM_TIME = 8 * 60        # total simulation time = 8 hours (in minutes)
OUTPUT_FILE = "call_center_results.csv"  # CSV file name


# Call Process
def call_process(env, name, agents, wait_times, service_times, queue_lengths):
    arrival_time = env.now
    queue_lengths.append(len(agents.queue))
    
    with agents.request() as req:
        yield req
        wait = env.now - arrival_time
        wait_times.append(wait)

        service_time = random.expovariate(1 / MEAN_SERVICE)
        service_times.append(service_time)
        yield env.timeout(service_time)


# Call Generator
def call_generator(env, agents, wait_times, service_times, queue_lengths):
    call_id = 0
    while True:
        inter_arrival = random.expovariate(ARRIVAL_RATE)
        yield env.timeout(inter_arrival)
        call_id += 1
        env.process(call_process(env, f"Call-{call_id}", agents, wait_times, service_times, queue_lengths))


# Main Simulation
def run_simulation(num_agents):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    agents = simpy.Resource(env, capacity=num_agents)

    wait_times = []
    service_times = []
    queue_lengths = []

    env.process(call_generator(env, agents, wait_times, service_times, queue_lengths))
    env.run(until=SIM_TIME)

    # Calculate metrics
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    avg_queue = statistics.mean(queue_lengths) if queue_lengths else 0
    throughput = len(service_times) / SIM_TIME
    utilization = (sum(service_times) / (num_agents * SIM_TIME))

    # Display results
    print("------------------------------------------------------")
    print(f"Results for {num_agents} Agents:")
    print(f"Average Wait (min): {avg_wait:.2f}")
    print(f"Average Queue Length: {avg_queue:.2f}")
    print(f"Throughput (calls/min): {throughput:.2f}")
    print(f"Utilization: {utilization:.3f}")
    print(f"Total Calls Arrived: {len(service_times)}")
    print("------------------------------------------------------")

    # --- Save results to CSV file ---
    # Check if file exists (to write header only once)
    file_exists = os.path.exists(OUTPUT_FILE)

    with open(OUTPUT_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Num_Agents", "Average_Wait(min)", "Average_Queue_Length",
                "Throughput(calls/min)", "Utilization", "Total_Calls"
            ])
        writer.writerow([
            num_agents, round(avg_wait, 2), round(avg_queue, 2),
            round(throughput, 2), round(utilization, 3), len(service_times)
        ])
    print(f"✅ Results saved to '{OUTPUT_FILE}'\n")


# Get user input and run
if __name__ == "__main__":
    try:
        num_agents = int(input("Enter number of agents: "))
    except ValueError:
        num_agents = 3
        print("Invalid input. Using default: 3 agents.")

    run_simulation(num_agents)
