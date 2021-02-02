# Takahashi's models of generalized exchange

The global information model, is an evolutionary model where each generation
goes throgh a series of trials. For each trial, an agent receives a fixed number of credits that
may or may not share with a neighboring agent. The agents connection is
complete, this means that each agent can give or receive from any other agent
from the model. For each trial, an agent will choose a neighbor to give a
number of its credits.

The neighbor and credits are defined by two state variables:
* The giving gene (gg) defines how many credits will give. This is an integer value
  between 0 and 10 (borders included).
* The tolerance gene (tg) defines how permisive it is with the neighboring altruism.
  Its value goes from 0.1 to 2 (borders included).
  During a trial, the agent will give to agents that have given at least
  tg\*gg. If there are no agents that have given such amount of credits in the
  previous trial it will give to the most giving agent.

Agents receive more credits than the credits given. In the case of this model
agents receive twice the given amount.

After all trials finish, the evolutionary process starts removing
all agents that their amount of total credits is smaller than the mean - std.
The agents with more than mean + std credits will spawn a new generation. The
ones that are between +/-std boundaries will remain during the next generation.

The new agents spawned into the generation has 95% chances to remain as they were.
A small percentage will go through a mutation of their gg and tg values.

The new agents are added to the model while the number of agents is smaller
than a fixed value (20 agents in accordance with the original model). Models
exceeding that number are not created. New connections are made following the
global model patterns.

Mapping to EB-DEVS
====================


AgentState:
  gg = rand int [0, 10]
  tg = rand  [0.1, 2]
  credits = 10
  
Init:
  ta = 0
  state = INIT
  share culture to neighbors

IntTransition:
  choose a random neighbor
  if random() < matching culture positions / culture lenth:
    mix cultures:
      find a random different position, copy this value to the transitioning model's culture
      share the state with neighbors.

ExtTransition:
  update {neighbor_id: culture}


Extension idea
================

* Use the hegemonic culture to mix towards it
  - Si mi cultura se aleja mean + sd
  - Comparar con resultado principal ya sea cambio de fase, cantidad de culturas, etc.


## Introduction

In 2000 Takahashi (2000) developed two ingenious agent-based models to explain
the emergence of generalised exchange among multiple agents under the
hypothesis of selective altruism based on fairness. In his article Takahashi
shows that his results are valid not only in artificial societies where
information is shared among all agents (i.e. global information) but also in
artificial societies where agents only know about their immediate neighbours
(i.e. local information).

The results obtained under the assumption of global information have been
corroborated by Edmonds and Hales (2005) even in more general conditions.
Edmonds and Hales (2005) also replicate Takahashi's (spatial) model of local
information and point out that the results obtained with this spatial model
contribute to the significant body of work supporting the idea that artificial
agents tend to deal better with Prisoner's dilemma type of games in spatial
contexts (Doebeli and Hauert 2005; Fort and Perez 2005; Nowak and May 1992;
Nowak and Sigmund 1998). The literature suggests that _context preservation in
general_ tends to promote cooperation in the Prisoner's dilemma (Cohen, Riolo
and Axelrod 1999; Gotts, Polhill and Law 2003) -a conclusion that has been
confirmed in other games (Nemeth and Takacs 2007) but does not necessarily
extend to all other social dilemmas (see e.g. Doebeli et al. 2005; Hauert and
Doebeli 2004)-.

## Model with global information

### Brief description

We start by analysing the model with global information. In Takahashi's (2000)
original model there are 20 agents who interact over some number of
generations. Each generation consists of a set of "trials". In each trial
every agent receives 10 units of resource and is given the option to donate as
many units as he wants to another agent. Thus, agents must decide how many
units to give and to whom. This decision is determined by the agent's genetic
code, which is divided into two parts:

* The giving gene, which is an integer in the range [0, 10] denoting the
  number of units that the agent will give.

* The tolerance gene, which is a multiple of 0.1 in the range [0.1, 2], and
  is used to identify the set of potential recipients. To be precise, an
  agent with giving gene _GG_ and tolerance gene _TG_ will only give to other
  agents who have given at least _GG_ * _TG_ units of resource in the
  previous trial. Thus, an agent with _TG_ > 1 will only give to agents who
  have donated more than he himself did, whereas an agent with _TG_ < 1 is
  prepared to give to others who donated less than he himself did. The
  donating agent chooses the recipient randomly among the set of other agents
  who satisfy the mentioned condition. 

The giving agent donates GG units of resource, but the recipient obtains _GG_
* _RV_ units. Thus, when _RV_ > 1 the receiver obtains a greater benefit than
the cost incurred by the giver, so the strategic situation becomes a social
dilemma (Dawes 1980).

At the end of each generation those agents who have obtained more units of
resource are replicated comparatively more frequently in the next generation.
The selection mechanism implemented in the evolutionary process is a
truncation method (De Jong 2006) similar to the mechanism used by Axelrod
(1986) in the metanorm games ([which is also analysed in this
appendix](./axelrod1986.html)): at the end of each generation two evolutionary
forces (natural selection and mutation) come into play to replace the old
generation with a brand new one:

  * The new generation is composed by the offspring of some of the players in
    the previous generation. Agents in the old generation with an amount of
    resource exceeding the population average by at least one standard
    deviation are replicated twice (i.e. they produce two offspring with the
    same genetic code as the parent, subject to mutation); players who are at
    least one standard deviation below the population average are eliminated
    without being replicated; and the rest of the players are replicated once.
    In the original paper Takahashi indicates that -for simplicity- he adjusts
    the group size to be constant, but he does not specify exactly how. Our
    analysis does not depend on the precise mechanism by which this adjustment
    occurs. 

  * The genetic code of each agent in each generation has a 5% chance of
    mutating. It is not clear whether both genes can simultaneously mutate or
    only one of them can change at a time. In any case, our analysis below is
    valid for either assumption. 

### The model as a time-homogeneous Markov chain

This model can be represented as a time homogeneous Markov chain by defining
the state of the system as the number of agents having a certain genetic code
at the beginning of each generation. The number of different genetic codes is
11\*20 = 220 (10 units of resource an agent can give plus the option of not
giving, times 20 different values for the tolerance gene). Thus the number of
possible states of the system is:

Number of possible states:  | ![Number of possible
states](Takahashi2000-1.png)  
---|---  
  
### Analysis

The mutation operator of this model guarantees that the induced THMC is
irreducible and aperiodic.

If both genes can change at the same time, the induced Markov chain satisfies
sufficient condition (i) for irreducibility and aperiodicity pointed out in
Proposition 4 of our paper:

Proposition 4     (i) If it is possible to go from any state to any other
state in one single time-step ( _p_ _i_ , _j_ > 0 for all _i_ ≠ _j_ ) and
there are more than 2 states, then the THMC is irreducible and aperiodic.

If only one gene can change at a time, then we can use sufficient condition
(iii) for irreducibility and aperiodicity:

Proposition 4     (iii) If there exists a positive integer _n_ such that _p_ (
_n_ ) _i_ , _j_ > 0 for all _i_ and _j_ , then the THMC is irreducible and
aperiodic.

In this model it is possible to go from any state _i_ to state _j_ in three
steps. The demonstration of this statement is simple when one realises that
one can go from any state _i_ to a state _i *_ where all agents have tolerance
gene as in state _i_ and giving gene _GG_ = 0. In that intermediate state _i
*_ every agent obtains the same units of resources so every agent is
replicated once. From state _i *_ it is possible to go to state _j *_, where
every agent has its tolerance gene as in state _j_ and its giving gene _GG_
still equal to 0. Again, every agent is replicated once. Finally, from state
_j *_ it is possible to go to state _j_.

Consequently, regardless of the precise way in which the mutation operator
works, the model is an irreducible and aperiodic THMC, also called ergodic.

As we have seen in the paper, in these processes the probability of finding
the system in each of its states in the long run is strictly positive and
independent of the initial conditions, and the limiting distribution π
coincides with the occupancy distribution π*. Although calculating such
probabilities from the transition matrix is rather impractical, we can
approximate them as much as we want by running just one simulation for long
enough.

Both Takahashi (2000) in his original paper and Edmonds and Hales (2005) in
their reimplementation conduct two experiments with this model: in one
experiment the agents' genetic code is initialised randomly and in the other
experiment every agent starts with giving gene _GG_ = 0. Both experiments
consist of 50 replications of 1000 generations each. The two groups of
researchers observe that the results obtained in both experiments are very
similar. Having proved that the long-run dynamics of the model are independent
of the initial conditions, the empirical results obtained by Takahashi (2000)
and by Edmonds and Hales (2005) suggest -but do not prove- that 50
replications of 1000 generations seem to be sufficient to approximate the
long-run dynamics of the model.

As we explain in section 9.2.1 of the paper, since the limiting and the
occupancy distribution coincide, another method to approximate the limiting
distribution would be to run just one simulation for long enough. We recommend
running various simulation runs starting from widely different initial
conditions to increase our confidence that the conducted simulations are long
enough to accurately approximate the limiting distribution.

## Model with local information

### Brief description

In the second model proposed by Takahashi (i.e. the spatial model with local
information only) there are 100 agents located on a square [1] grid of 10×10
cells. Each agent only interacts with his local neighbours (Moore
neighbourhood of radius 1). The selection mechanism is different from that in
the non-spatial model: at the end of each generation, if an agent has any
neighbour with more units of resource than himself, then he adopts the genetic
code of the most successful agent in his neighbourhood. Updating of genetic
codes takes place synchronously.

### Analysis of the model as a time-homogeneous Markov chain

Again, the state space in this second model can be defined as the set of
different genetic codes that an agent may have. With this definition, the
model has 220100 different states! Assuming that the model includes a
probability of mutation for every agent's genetic code in each generation, we
can state -for the same reasons discussed above- that the local information
model is also ergodic.

## References

AXELROD R M (1986) An Evolutionary Approach to Norms. _American Political
Science Review_ , 80(4), pp. 1095-1111

COHEN M D, Riolo R L, and Axelrod R M (1999) The Emergence of Social
Organization in the Prisoner's Dilemma: How Context-Preservation and Other
Factors Promote Cooperation. _Santa Fe Institute Working Paper_ , 99-01-002,

DAWES R M (1980) Social Dilemmas. _Annual Review of Psychology_ , 31, pp.
161-193

DE JONG K A (2006) _Evolutionary computation. A unified approach_. Cambridge,
Mass: MIT Press.

DOEBELI M and Hauert C (2005) Models of cooperation based on the Prisoner's
Dilemma and the Snowdrift game. _Ecology Letters_ , 8(7), pp. 748-766

EDMONDS B and Hales D (2005) Computational Simulation as Theoretical
Experiment. _Journal of Mathematical Sociology_ , 29(3), pp. 209-232.

FORT H and Perez N (2005) The Fate of Spatial Dilemmas with Different Fuzzy
Measures of Success. _Journal of Artificial Societies and Social Simulation_ ,
8(3)1. <http://jasss.soc.surrey.ac.uk/8/3/1.html>.

GOTTS N M, Polhill J G, and Law A N R (2003) Agent-based simulation in the
study of social dilemmas. _Artificial Intelligence Review_ , 19(1), pp. 3-92

HAUERT C and Doebeli M (2004) Spatial structure often inhibits the evolution
of cooperation in the snowdrift game. _Nature_ , 428(6983), pp. 643-646

NÉMETH A and Takacs K (2007) The Evolution of Altruism in Spatially Structured
Populations. _Journal of Artificial Societies and Social Simulation_ , 10(3)4.
<http://jasss.soc.surrey.ac.uk/10/3/4.html>.

NOWAK M A and May R M (1992) Evolutionary Games and Spatial Chaos. _Nature_ ,
359(6398), pp. 826-829

NOWAK M A and Sigmund K (1998) Evolution of indirect reciprocity by image
scoring. _Nature_ , 393(6685), pp. 573-577

TAKAHASHI N (2000) The emergence of generalized exchange. _American Journal of
Sociology_ , 10(4), pp. 1105-1134

* * *

1 The lattice is not a torus; agents on the edges and agents at the corners
have fewer neighbours than agents in central positions.

