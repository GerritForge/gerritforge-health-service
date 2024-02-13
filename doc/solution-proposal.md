# Solution proposal

The proposed solution is based on the [Horizontal and Vertical Scaling of Container-based
Applications using Reinforcement Learning](http://www.ce.uniroma2.it/publications/cloud2019.pdf)
paper, which is trying to solve a comparable issue to the one we are trying
to solve.

From the paper:

> Differently from the popular threshold-based approaches used to drive elasticity, we aim to design a flexible approach that can customize the adaptation policy without the need of manually tuning various configura- tion knobs.

This is the exact aim we are after with GHS.

## Model definition

To properly process increasing incoming traffic and keep
the system performance stable,  some maintenance operations have
to be carried out on the git repository.
Gerrit exposes several metrics, among which is the upload-pack response time.
A targeted response time ($ R_{max} $) that should not be exceeded will be defined.

When performing any maintenance operation on a repository, performance penalties,
for example, a system load increase is paid.
Triggering proper maintenance operations  avoids exceeding the
pre-defined target response.

## States

$S$ will represent the _state space_.

We define the state at time $\text{\i}$ as $s_i=(l_i, n_i, b_i)$, where:
* $l_i$: system load
* $n_i$: number of pack files
* $b_i$: bitmap index misses

All the metrics used to define our state are real numbers.
We will "discretize" them by binning them with a range suitable
for the different metrics.

## Actions

$A$ will represent the _actions space_.

We will start with three simple actions:
* $none$: no action performed
* $gc$: garbage collection (with only gc.prunePackExpire and gc.prunePack [parameters](https://git.eclipse.org/r/plugins/gitiles/jgit/jgit/+/725e77a5176384ff55195a302888cd661440a031/Documentation/config-options.md#gc-options)). Expensive action with "far-sighted" effect.
* $bitmap$: create bitmaps. Cheap action with a "short-sighted" effect.

## Cost function

The cost function $c(s, a, s')$, captures the cost of carrying out action $a$
when the application state transits from $s$ to $s'$.

We can define the cost in terms of:
* performance penalty $c_{perf}$: paid when upload-pack response exceeds $R_{max}$;
* resource cost $c_{res}$: time taken to complete the action

We can combine the costs into a single weighted cost:

$c(s, a, s')=w_{perf} \cfrac{ count(R(l, n, b) > R_{max}) * c_{perf} }{c_{perf}} + w_{res} \cfrac{ timeelapsed(a)}{T_{max}}$

where $w_{perf} + w_{res} = 1$ and $w_{perf} >= 0$, $w_{res} >=0 $.
$R(l, n, b)$ is the response time in state $s=(l, n, b)$.

## Algorithms

We can start with a _model-free_ algorithm, like [Q-learning](https://en.wikipedia.org/wiki/Q-learning).

It will be simpler to implement compared to a _model based_ one
and will allow to start exploring and validating our model definition. 
The price to pay will be a long learning phase.

We can consider delayed rewards models, like [RUDDER](https://github.com/widmi/rudder-a-practical-tutorial),
to factor in the time consuming operations normally used for repository maintenance.
[Here](https://github.com/widmi/rudder-a-practical-tutorial) a Pytorch
example of [delayed reward](https://github.com/widmi/rudder-a-practical-tutorial).

We can then evolve to a more sophisticated _model-based_ approach,
where we will need to capture the knowledge of the system
dynamics in a probability function $p(s’|s,a)$ expressing the
estimated resource utilization per _state-action_ pair.

### Q-learning

We will use [epsilon greedy](https://www.baeldung.com/cs/epsilon-greedy-q-learning).

These are the Q-learning hyperparameters:
* [learning rate](https://www.baeldung.com/cs/epsilon-greedy-q-learning#1-alpha-boldsymbolalpha)
* [discount factor](https://www.baeldung.com/cs/epsilon-greedy-q-learning#2-gamma-boldsymbolgamma)
* [epsilon](https://www.baeldung.com/cs/epsilon-greedy-q-learning#3-epsilon-boldsymbolepsilon)

### Model based RL

For this model we will need to estimate the $p(s’|s,a)$, CPU utilization transition
probabilities from a state to another caused by an action.

# Tooling

* ML/RL framework: [Pytorch](https://pytorch.org/)
* Build simulation/testing environment: [Gymnasium](https://github.com/Farama-Foundation/Gymnasium)
* Notebook: [Jupyter](https://jupyter.org/)
* Model monitoring and visualization: [TensorBoard](https://www.tensorflow.org/tensorboard)
* Pythorch with TensorBoard: [Pytorch util](https://pytorch.org/docs/stable/tensorboard.html)

# References

* [Custom environment for trading algorithm](https://medium.com/@sthanikamsanthosh1994/custom-gym-environment-stock-trading-for-reinforcement-learning-stable-baseline3-629a489d462d)
* [Custom environment for heard pole](https://github.com/vadim0x60/heartpole/tree/master)

