# Result Analysis

Based on the actual measured workload data from Locust and Docker stats, the following observations have been made:

**1. How does average response time change as concurrency increases?**
Average response time increases gradually from W1 to W4 (28 ms up to 60 ms), but at W5 (16 concurrent users), it sharply jumps to 152 ms, indicating performance saturation under higher load.

**2. How does throughput change?**
Throughput scales almost linearly initially: 4.19 req/s at 1 user, 8.59 req/s at 2 users, and 14.77 req/s at 4 users. It continues to increase, reaching 43.48 req/s at 16 concurrent users.

**3. Are there failed requests?**
No. Across all workloads (W1-W5), there are 0 failed requests.

**4. Which service has the highest CPU utilization?**
The Student Service clearly consumes the most CPU. At W5, its average CPU usage was 47.34% with a peak of 79.06%, compared to only 3.21% avg for Course Service and 3.99% avg for Result Service. This is because Student Service acts as an orchestrator, handling E2E requests and managing outgoing async HTTP connections to the other two services.

**5. Which service has the highest memory utilization?**
The Student Service consumes the most memory (averaging around ~94.5 MiB). Course Service and Result Service maintain lower memory footprints (both ~30 MiB).

**6. How does CPU change as workload increases?**
CPU usage scales upwards with the workload. For example, Student Service average CPU starts at 6.96% for W1 and rises steadily to 47.34% for W5.

**7. How does memory change as workload increases?**
Memory consumption remains relatively stable and flat across all workloads. Student service hovers around 94-95 MiB, and Course/Result services hover around 30 MiB, regardless of the workload size.

**8. At which workload does performance degradation become noticeable?**
Performance degradation becomes noticeable at **W5** (16 concurrent users). At this point, the average response time jumps by more than 2.5x compared to W4 (from 60 ms to 152 ms). 

**9. Are there any response-time outliers?**
The measured data shows an outlier, but the exact cause cannot be established from the available measurements. In W3 (4 concurrent users), the maximum response time recorded was 1836 ms, which is significantly higher than the average of 47 ms.

**10. Are there any failures?**
There were no request failures throughout the test. All 2915 total requests returned successfully.

**11. What is the overall performance conclusion?**
The system architecture works well and successfully manages inter-service communication without failures under the tested load. However, the `student-service` is the bottleneck in the system because it must orchestrate external network calls for every request to the dashboard. To handle larger loads, scaling the Student Service instances and optimizing the E2E aggregation logic should be prioritized.
