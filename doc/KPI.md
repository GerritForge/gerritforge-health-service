# Evaluation Metrics

To evaluate the effectiveness of proposed models, we plan to compute two (families of) metrics.

## Area of Lift

For each clone and fetch activity generated during the evaluation, we store: (a) the timestamp when the event occurred; and (b) the performance score (e.g., time spent during the search for reuse phase). Each activity can be plotted on a cartesian plane in the unit square space by normalizing the timestamp by the earliest and latest observations, and normalizing the performance score by either its maximium observed value during the evaluation or its clipped maximum setting. Each proposed approach (e.g., no-action baseline, RL models, rule-based approaches) can then be plotted as different curves in the unit square space. Inspired by lift charts (a.k.a., [Alberg diagrams](https://doi.org/10.1109/32.553637)), we can then compute and compare areas under these curves to compare approaches. For example, a learned or rule-based approach can be evaluated by subtracting the area under its curve from the area under the worst-case (no-action) model. The result can be normalized by the area under the worst-case model, such that a zero score indicates the worst possible performance and one indicate (theoretical) perfect performance (not practical attainable).

## Number of Events Avoided

For each approach that is being evaluated, we will track the number of times that the system raises an alarm due to its performance becoming of concern. We will also indicate if an approach crosses a "point of no return", where the system becomes so overburdened that performing any recovery action is impossible without incurring downtime.
