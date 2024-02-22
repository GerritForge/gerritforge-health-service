# GerritForge AI Health Service (aka GHS)

AI service for keeping a Gerrit and Git system healthy, using an intelligent [RLHF Model](https://en.wikipedia.org/wiki/Reinforcement_learning_from_human_feedback)
trained with performance metrics coming from [GerritHub](https://review.gerrithub.io).

## The problem: How do we maintain Gerrit and Git SCM healthiness and stability?

Gerrit Code Review and other Git servers have become more and more stable and reliable over the years,
which should sound reassuring for all of those companies that are looking at a reduced staff and the
challenge of keeping the lights on of the SCM.
However, the major cause of disruption is represented by what is not linked to the SCM code but rather
its data.

The Git repositories and their status are nowadays responsible for 80% of the stability issues with
Gerrit and possibly with other Git servers as well.
Imagine a system that is receiving a high rate of Git traffic (e.g. Git clone) of 100 operations
per minute, and the system is able to cope thanks to a very optimised repository and bitmaps.
However, things may change quickly and some of the user actions (e.g. a user performing a force-push
on a feature branch) could invalidate the effectiveness of the Git bitmap and the server will start
accumulating a backlog of traffic.

In a fully staffed team of SCM administrators and with all the necessary metrics and alerts in place,
the above condition would trigger a specific alert that can be noticed, analysed, and actioned swiftly
before anyone notices any service degradation.

However, when there is a shortage of Git SCM admins, the number of metrics and alerts to keep under
control could be overwhelming, and the trade-offs could leave the system congestion classified as a
lower-priority problem.

When a system congestion lasts too long, the incoming tasks queueing could reach its limits,
and the users may start noticing issues. If the resource pools are too congested, the system could
also start a catastrophic failure loop where the workload further reduces the fan out of the execution
pool and causing soon a global outage.

The above condition is only one example of what could happen to a Git SCM system, but not the only one.
There are many variables to take into account for preventing a system from failing; the knowledge and
experience of managing them is embedded in the many of the engineers that are potentially laid off,
with the potential of serious consequences for the tech companies.

## GerritForge brings AI to the rescue of Gerrit Code Review and Git SCM stability

GerritForge has been active in the past 14 years in making the Git SCM system more suitable for enterprises
from its very first inception: that’s the reason why this blog is named “GitEnterprise” after all.

We have been investing over 2022 and 2023 in analysing, gathering and exporting all the metrics of the
Git repositories to the eyes and minds of the SCM administrators, thanks to open-source products like
Git repo-metrics plugin. However, the recent economic downturn could leave all the knowledge and value
of this data into a black hole if left in its current form.

When the work of analysing, monitoring and taking action on the data becomes too overwhelming for the
size of the SCM Team left after the layoffs, there are other AI-based tools that can come to the rescue.
However, none of them is available “out of the box” and their setup, maintenance and operation could also
become an impediment.

GerritForge has a historic know-how on knowledge-based systems and has been lecturing the community about
data collection and analysis for many years in the Gerrit Code Review community, for example the Gerrit
DevOps Analytics initiative back in 2017. It is now the right time to push on these technologies and
package them in a form that could be directly usable for all those companies who need it now.

## How GerritForge AI Health Service (aka GHS) can help?

As part of our 2024 goals, GerritForge will release a brand-new service called GHS, directly addressing
the needs of all companies that need to have a fully automated intelligent system for collecting,
analysing and acting on the Git repository metrics.

The high-level description of the service has already been anticipated at the Gerrit User Summit 2023
in Sunnyvale by Ponch and the first release of the product is due in Q1 of 2024.

### How does GHS work?

GHS is a multi-stage system composed of four basic processes:

1. Collect the metrics of your Gerrit or other Git repositories automatically and publish them on your
   registry of choice (e.g. Prometheus)
3. Combine the repository metrics with the other metrics of the system, including the CPU, memory and
   system load, automatically.
5. Detect dangerous situations where the repository or the system is starting to struggle and suggest
   a series of remediation policies, using the knowledge base and experience of GerritForge’s Team
   encoded as part of the AI engine.
7. Define a direct remediation plan with suggested priorities and, if requested, act on them automatically,
   assessing the results.

Stage 4, the automatic execution of the suggested remediation, can be also performed in cooperation
with the SCM Administrators’ Team as it may need to go through the company procedures for its execution,
such as change-management process or communication with the business.

However, if needed, point 4. can also be fully automated to allow GHS to act in case the SCM admins do
not provide negative feedback on the proposed actions.

### What are the benefits of GHS for the SCM team?

GHS is the natural evolution of GerritForge’s services, which have historically been proactive in the
analysis of the Git SCM data and the proposal of an action plan. The GerritForge’s Health Check is a
service that we have been successfully providing for years to our customers; the GerritForge Health
Service is the completion of the End-to-End stability that the SCM Team needs now more than ever,
to survive with a reduced workforce.

- To the SCM Administrator, GHS provides the metrics, analysis and tailored recommendations in real-time.
- To the Head of SCM and Release Management Team, GHS gives the peace of mind of keeping the system
  stable with a reduced workforce.
- To the SCM users and developers, GHS provides a stable and responsive system throughout the day,
  without slowdowns or outages
- To the Head of IT, GHS allows to satisfy the company’s needs of costs and head count reduction
  without sacrificing the overall productivity of the Teams involved.

## How does the GHS AI Engine works?

GHS AI Engine is based on a [Reinforcement Learning with Human Feedback Model](/doc/rlhf.md).

## Where do we start? The GHS MVP

There is no better way to start than building an initial MVP that could help us understand
better all the fundamental problems associated with the AI models applied to Git and Gerrit repositories
and explore different options.

See more details on the [GHS MVP definition](MVP.md).
