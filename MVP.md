# Minimal Viable Product - Inception

As with every new project, we need to kickstart with a minimum scope that
would still deliver a substantial value for all of those who are willing
to install and experiment GHS!

1. The scope of this MVP needs to be small enough to fit a 5-days
   hackathon of 5 people to fully implement and deliver to production
   on GerritHub.io.

2. The value needs to be tangible and higher than any other open-source
   products available and having the same purpose.

3. It needs to be _packaged_ in a way that is easily deployable to
   any Git or Gerrit systems (choose one of the two).

## Context

Git and Gerrit's admins have limited time and often too many things to
keep under control. The shire volume of logs, analytics, and possible
operational actions are often overwhelming, forcing the admin to fire-fight
most of the time and leaving little or no space at all for more constructing
and design work.

## The problem

The problem that we want to target is to allow a limited group of
Git or Gerrit admins to keep one repository under control and automatically
adjust its settings to keep its organization healthy and the
git-upload-pack performance stable.

Often, developers outnumber the abilities of the Gerrit admins to keep track
on how the traffic evolves and the repositories are changing shape, causing
production spikes in latency and explosions in the Git data.

## The MVP scope for GHS

GHS needs to allow the Git or Gerrit admin to automatically collect metrics:

1. Define which repository needs to be controlled and managed by GHS
2. Collect and track the metrics of the repository
3. Collect and track the Git protocol-level metrics of the git-upload-pack
   operations on the repository:
   - Git negotiation time
   - Counting
   - Search for reuse/sizes
   - Bitmap misses
   - Writing packfiles
   - Total execution time
4. Collect and track the CPU and System utilization metrics

GHS can perform one of the following actions on the repository:

1. Remove empty directories
2. Repack refs
3. Rebuild the bitmap
4. Perform a full GC
5. Do nothing

GHS needs to analyze on a regular basis (e.g., every 10 mins) the
repository and system metrics and understand which action is more
likely to provide an improvement to the system.

## Approach to the decision model

The decision model for selecting the actions based on the repository
and system metrics is a _black box_ with the following Input and Output:

*Decision Model - Inputs*

- The history of all previous decisions, with the associated outcomes
- The current metrics and delta from the last observation
- The available actions

*Decision Model - Outputs*

- A set of pairs of (A,P) where A is one of the GHS actions and P is the
  probability (between 0 = not likely at all, 1 = certainty) that the action
  would improve one or more of the system metrics.

It will be up to the Team of 5 developers to experiment and decide which model
would achieve the best results.

## AI Models

There are two candidate AI models for implementing the GHS decisions:

- [Reinforcement Learning](doc/rlhf.md), model-free or model-based, is an AI
  technique for improving the abilities of the domain to predict and decide
  the best action to achieve the optimal result, based on a reward function.

- [Fuzzy Logic](https://pypi.org/project/fuzzylogic/) where the probabilities
  of the input variables can be combined to calculate a probable outcome
  with associated distributions.

## MVP success criteria

We consider the MVP of GHS successful *IF* after 4-weeks of observation
on GerritHub.io, on the most active repository, we observe that the actions
taken have improved overall the performance of the git-upload-pack or not.