import pandas as pd
import matplotlib.pyplot as plt
import os

# Create directories
os.makedirs("results", exist_ok=True)
os.makedirs("results/graphs", exist_ok=True)

# Read performance results
perf_df = pd.read_csv("results/performance_results.csv")
perf_df.rename(columns={
    "workload": "Workload", 
    "concurrent_users": "Concurrency", 
    "requests": "Total Requests",
    "failed": "Failed Requests",
    "average_response_ms": "Average Response Time (ms)",
    "throughput_rps": "Throughput (req/s)"
}, inplace=True)
perf_df = perf_df[["Workload", "Concurrency", "Total Requests", "Failed Requests", "Average Response Time (ms)", "Throughput (req/s)"]]

# Read resource observations
res_df = pd.read_csv("results/resource_observations.csv")

# Clean data
res_df["cpu_percent"] = res_df["cpu_percent"].str.rstrip("%").astype(float)
res_df["memory_usage"] = res_df["memory_usage"].str.split("MiB").str[0].astype(float)

# Group and calculate metrics
res_summary = []
for workload in ["W1", "W2", "W3", "W4", "W5"]:
    w_df = res_df[res_df["workload"] == workload]
    row = {"Workload": workload}
    for service in ["student-service", "course-service", "result-service"]:
        s_df = w_df[w_df["container"] == service]
        prefix = service.split("-")[0].capitalize()
        row[f"{prefix} Avg CPU (%)"] = round(s_df["cpu_percent"].mean(), 2)
        row[f"{prefix} Peak CPU (%)"] = round(s_df["cpu_percent"].max(), 2)
        row[f"{prefix} Avg Memory (MiB)"] = round(s_df["memory_usage"].mean(), 2)
    res_summary.append(row)

res_summary_df = pd.DataFrame(res_summary)

# Merge
final_df = pd.merge(perf_df, res_summary_df, on="Workload")

# Reorder columns as required
cols = [
    "Workload", "Concurrency", "Total Requests", "Average Response Time (ms)", "Throughput (req/s)", "Failed Requests",
    "Student Avg CPU (%)", "Student Peak CPU (%)", "Student Avg Memory (MiB)",
    "Course Avg CPU (%)", "Course Peak CPU (%)", "Course Avg Memory (MiB)",
    "Result Avg CPU (%)", "Result Peak CPU (%)", "Result Avg Memory (MiB)"
]
final_df = final_df[cols]
final_df.to_csv("results/final_observation_table.csv", index=False)

# Graphs
plt.figure(figsize=(10,6))
plt.plot(final_df["Concurrency"], final_df["Average Response Time (ms)"], marker="o")
plt.xlabel("Concurrent Requests")
plt.ylabel("Average Response Time (ms)")
plt.title("Concurrent Requests vs Average Response Time")
plt.grid(True)
plt.savefig("results/graphs/concurrent_vs_response_time.png")
plt.close()

plt.figure(figsize=(10,6))
plt.plot(final_df["Concurrency"], final_df["Throughput (req/s)"], marker="o")
plt.xlabel("Concurrent Requests")
plt.ylabel("Throughput (req/s)")
plt.title("Concurrent Requests vs Throughput")
plt.grid(True)
plt.savefig("results/graphs/concurrent_vs_throughput.png")
plt.close()

plt.figure(figsize=(10,6))
plt.plot(final_df["Concurrency"], final_df["Student Avg CPU (%)"], marker="o", label="Student Service")
plt.plot(final_df["Concurrency"], final_df["Course Avg CPU (%)"], marker="o", label="Course Service")
plt.plot(final_df["Concurrency"], final_df["Result Avg CPU (%)"], marker="o", label="Result Service")
plt.xlabel("Concurrent Requests")
plt.ylabel("CPU Utilization (%)")
plt.title("Concurrent Requests vs CPU Utilization")
plt.legend()
plt.grid(True)
plt.savefig("results/graphs/concurrent_vs_cpu.png")
plt.close()

plt.figure(figsize=(10,6))
plt.plot(final_df["Concurrency"], final_df["Student Avg Memory (MiB)"], marker="o", label="Student Service")
plt.plot(final_df["Concurrency"], final_df["Course Avg Memory (MiB)"], marker="o", label="Course Service")
plt.plot(final_df["Concurrency"], final_df["Result Avg Memory (MiB)"], marker="o", label="Result Service")
plt.xlabel("Concurrent Requests")
plt.ylabel("Memory Utilization (MiB)")
plt.title("Concurrent Requests vs Memory Utilization")
plt.legend()
plt.grid(True)
plt.savefig("results/graphs/concurrent_vs_memory.png")
plt.close()

# CPU and Memory separate service bar charts
plt.figure(figsize=(10,6))
width = 0.25
x = final_df["Concurrency"].to_numpy()
plt.bar(x - width, final_df["Student Avg CPU (%)"], width, label="Student")
plt.bar(x, final_df["Course Avg CPU (%)"], width, label="Course")
plt.bar(x + width, final_df["Result Avg CPU (%)"], width, label="Result")
plt.xlabel("Concurrent Requests")
plt.ylabel("Average CPU (%)")
plt.legend()
plt.title("Average CPU per Service")
plt.xticks(x)
plt.savefig("results/graphs/cpu_per_service.png")
plt.close()

plt.figure(figsize=(10,6))
plt.bar(x - width, final_df["Student Avg Memory (MiB)"], width, label="Student")
plt.bar(x, final_df["Course Avg Memory (MiB)"], width, label="Course")
plt.bar(x + width, final_df["Result Avg Memory (MiB)"], width, label="Result")
plt.xlabel("Concurrent Requests")
plt.ylabel("Average Memory (MiB)")
plt.legend()
plt.title("Average Memory per Service")
plt.xticks(x)
plt.savefig("results/graphs/memory_per_service.png")
plt.close()

print("Graphs and final observation table generated successfully.")
