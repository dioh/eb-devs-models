Axelrod dissemination of culture
---------------------------------

[Interesting link with implementation]( http://jasss.soc.surrey.ac.uk/12/1/6/appendixB/Axelrod1997.html)

Details
=========

Each agent has a state with two vector variables. A cultural trait array with
size 5 and each position with values between 1 and 10, and a similarity integer
with range 0 to 4.  Agents state's change with interactions. Given an agent and
its linked neighbors, the agent picks one neighbor to mix its culture with. If
their similarity, defined as the average of equal cultural features is bigger
than a random value, then the process of cultura mixing starts. The process of
cultural mix is done by choosing one of the different features in the culture
array and agreeing to the same value.

### Ajustar y que no se escapen detalles de conectividad por ejemplo

Originally, links between agents are defined by proximity in the 2d plane.

According to axelrod:

    The methodology of the present study is based on three principles:

    1. Agent-based modeling. Mechanisms of change are specified for local actors,
       and then consequences of these mechanisms are examined to discover the
       emergent properties of the system when many actors interact.3 simulation is
       especially helpful for Computer this bottom-up but its use predates the
       availability of personal computers approach, (e.g., Schelling 1978).
    2. No central authority. Consistent with the agent-based approach is the lack
       of any central coordinating agent in the model. It is certainly true that
       important aspects of cultures sometimes come to be standardized, canonized,
       and disseminated by powerful authorities such as church fathers, Webster,
       and Napoleon. The present model, however, deals with the process of social
       influence before (or alongside of) the actions of such authorities.  It
       seeks to understand and stability can just how much of cultural emergence to
       the coordinating be explained without resorting influence of centralized
       authority.
    3. Adaptive rather than rational agents. The individuals are assumed to follow
       simple rules about giving and receiving influence. These rules are not
       necessarily derivable from any of rational calculation based on costs and
       benefits or forward-looking principles strategic analysis typical of game
       theory. Instead, the agents simply adapt to their environmen

Mapping to EB-DEVS
====================


AgentState:
  {neighbor_id: culture}
  self.culture
  
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

