turtles-own [
  ;; Axelrod Culture Dissemination model
  culture     ;; vector of length 5, containing values 1~10
  similarity  ;; an integer between 0 and 4
]

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; AGENT INITIALIZATION ;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

to initialize-axelrod 
  ask turtles [
    set similarity 0
    set culture n-values 5 [(random 9) + 1]
  ]
  ask turtles [
    set-similarity
    do-coloring ]
end

to set-similarity
  set similarity 0
  foreach (sort link-neighbors)
  [set similarity similarity + (similarity-between ? self)]
end

to do-coloring 
  set color 109.9 - (2 * similarity)
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;    UPDATE RULES   ;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
to go
  ifelse simultaneous?
  [ask turtles
  [ let neighbor one-of link-neighbors
    if random-float 1 < (similarity-between neighbor self) [interact-with neighbor]
    set-similarity 
    do-coloring]]
  [ask one-of turtles
  [ let neighbor one-of link-neighbors
    if random-float 1 < (similarity-between neighbor self) [interact-with neighbor]
    set-similarity 
    do-coloring]]
  tick
end

to-report similarity-between [turtle1 turtle2]
  let culture1 [culture] of turtle1
  let culture2 [culture] of turtle2
  let same 0
  ;; if the two lists contain the same traits, increase similarity
  ( foreach culture1 culture2  
  [ if ?1 = ?2 [set same same + 1] ] )
  report (same / 5) ;; since 5 traits
end

to-report different-features [turtle1 turtle2]
  let culture1 [culture] of turtle1
  let culture2 [culture] of turtle2
  let values (list)
  
  foreach n-values 5 [?]
  [ if (item ? culture1 != item ? culture2)
    [ set values lput ? values ] ]
  report values
end

;; select at random a feature on which the active site and its neighbor 
;; differ (if there is one) and changing the active site's trait on this feature 
;; to the neighbor's trait on this feature
to interact-with [neighbor] ;; patch procedure
  if similarity-between self neighbor != 1
  [ 
    let index one-of (different-features self neighbor)
    let new-feature item index [culture] of neighbor
    set culture replace-item index culture new-feature
  ]
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;   COLORING RULES   ;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

to recolor
  let different-cultures remove-duplicates [culture] of turtles
  foreach different-cultures
  [ ask turtles with [culture = ?] [set color 1 + position ? different-cultures] ]
  display
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; NETWORK STRUCTURES ;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

to setup-patch-lattice
end

to setup-lattice [len dim] ;; called Lattice
  __clear-all-and-reset-ticks
  crt len ^ dim 
  initialize-axelrod
  ask turtles [
    let id [who] of self
    let coordinates []
    let temp 0
    let target (turtle-set)
    
    foreach n-values dim [? + 1] [
      set coordinates lput (id mod len ^ ? / len ^ (? - 1)) coordinates 
      set id id - (id mod len ^ ?)
    ]
    ;; we want to add one to each coordinate, then create links with those coordinates
    foreach n-values dim [?] [
      let temp-coordinates replace-item ? coordinates (item ? coordinates + 1) ;; add 1 to one of the coordinates

      if item ? temp-coordinates >= len [ set temp-coordinates replace-item ? temp-coordinates 0 ]

      
      foreach n-values dim [?] [
        set temp temp + item ? temp-coordinates * len ^ ?   ;; retrieve the turtle number from coordinates
      ]

      set target (turtle-set target turtle temp)
      set temp 0
    ]
    create-links-with target
  ]
end

to setup-fully-connected ;; called Mean Field
  __clear-all-and-reset-ticks
  crt N 
  initialize-axelrod
  ask turtles [create-links-with other turtles]
end

to setup-random ;; called Random
  __clear-all-and-reset-ticks
  crt N 
  initialize-axelrod
  ask turtles [create-link-with one-of other turtles]
end

to setup-small-world ;; called Small World
  __clear-all-and-reset-ticks
  crt N 
  initialize-axelrod
  ask turtles [ set shape "circle" ]
  layout-circle (sort turtles) max-pxcor - 1
  let c 0
  while [c < count turtles]
  [  ask turtle c [create-link-with turtle ((c + 1) mod count turtles)]
      set c c + 1
  ]
end

to setup-preferential ;; called Scale Free
  __clear-all-and-reset-ticks 
  create-initial-nodes
  repeat N - m0 [make-node-with preferential-group] 
  initialize-axelrod
end

to create-initial-nodes
  repeat m0 
  [ make-node-with one-of other turtles ]; with [not link-neighbor? self] ] ;;do we need this part?
end

;; Idea: first create a function that takes two turtles as inputs and when executed, links the two
;; Next, repeat N times the following: create new node, link to m separate lottery winners
to make-node [arg]
  crt arg
end
    
;; used for creating a new node.
;; if TARGET is a single agent, link with that agent
;; if TARGET is a set of agents, link with all agents.
to make-node-with [target]
  make-node 1
  ask max-one-of turtles [who] ;; the last turtle added
  [ if target != nobody
      [ if is-agent? target 
        [ create-link-with target [ set color gray ] 
          move-to target ]
        if is-agentset? target 
        [ create-links-with target[ set color gray ] 
          move-to one-of target ]
        ;; position the new node near its partner
        fd 20 ] ]
end

to-report preferential-group
  ;; connect the turtle to m number of partners
  ;; start by creating one target
  let targets (turtle-set find-partner)
  repeat (m - 1) 
  [ let next-node find-partner
    
    ;; add a target that is not already a target
    while [member? next-node targets]
      [set next-node find-partner ]
    
    set targets (turtle-set targets next-node) ]
  report targets
end
  

;; This code is borrowed from Lottery Example (in the Code Examples
;; section of the Models Library).
;; The idea behind the code is a bit tricky to understand.
;; Basically we take the sum of the degrees (number of connections)
;; of the turtles, and that's how many "tickets" we have in our lottery.
;; Then we pick a random "ticket" (a random number).  Then we step
;; through the turtles to figure out which node holds the winning ticket.
to-report find-partner
  let total random-float sum [count link-neighbors] of turtles
  let partner nobody
  ask turtles
  [ let nc count link-neighbors
    ;; if there's no winner yet...
    if partner = nobody
    [ ifelse nc > total
        [ set partner self ]
        [ set total total - nc ] ] ]
  report partner
end

to-report limit-magnitude [number limit]
  if number > limit [ report limit ]
  if number < (- limit) [ report (- limit) ]
  report number
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;    LAYOUT      ;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

to layout
  ;; the number 3 here is arbitrary; more repetitions slows down the
  ;; model, but too few gives poor layouts
  repeat 3  [
    ;; the more turtles we have to fit into the same amount of space,
    ;; the smaller the inputs to layout-spring we'll need to use
    let factor sqrt count turtles
    ;; numbers here are arbitrarily chosen for pleasing appearance
    layout-spring turtles links (1 / (factor)) (7 / factor) (7 / factor)
    display  ;; for smooth animation
  ]
  ;; don't bump the edges of the world
  let x-offset max [xcor] of turtles + min [xcor] of turtles
  let y-offset max [ycor] of turtles + min [ycor] of turtles
  ;; big jumps look funny, so only adjust a little each time
  set x-offset limit-magnitude x-offset 0.1
  set y-offset limit-magnitude y-offset 0.1
  ask turtles [ setxy (xcor - x-offset / 2) (ycor - y-offset / 2) ]
end

to resize-nodes
  ifelse all? turtles [size <= 1]
  [ ;; a node is a circle with diameter determined by
    ;; the SIZE variable; using SQRT makes the circle's
    ;; area proportional to its degree
    ask turtles [ set size sqrt count link-neighbors ] ]
  [ ask turtles [ set size 1 ] ]
end
@#$#@#$#@
GRAPHICS-WINDOW
210
10
798
619
20
20
14.1
1
10
1
1
1
0
0
0
1
-20
20
-20
20
0
0
1
ticks
30.0

BUTTON
10
35
117
68
Lattice
setup-lattice cube-length dimension
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
10
395
182
428
dimension
dimension
0
10
3
1
1
NIL
HORIZONTAL

SLIDER
10
430
182
463
cube-length
cube-length
0
50
7
1
1
NIL
HORIZONTAL

SLIDER
10
465
182
498
N
N
0
1000
96
1
1
NIL
HORIZONTAL

BUTTON
10
75
97
108
Mean Field
setup-fully-connected
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
100
75
200
108
Random
setup-random
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
75
180
142
213
Layout
layout
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
10
180
73
213
Go
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
10
285
82
318
Recolor
recolor
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

PLOT
805
15
1070
225
Distinct cultures
NIL
NIL
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot length remove-duplicates [culture] of turtles"

BUTTON
10
110
97
143
Scale Free
setup-preferential
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
10
500
182
533
m0
m0
0
5
3
1
1
NIL
HORIZONTAL

SLIDER
10
535
182
568
m
m
0
5
2
1
1
NIL
HORIZONTAL

BUTTON
85
285
187
318
Resize
resize-nodes
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
10
320
122
353
radial-central
layout-radial turtles links max-one-of turtles [count link-neighbors]
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
100
110
200
143
Small World
setup-small-world
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SWITCH
10
220
142
253
simultaneous?
simultaneous?
1
1
-1000

TEXTBOX
10
165
160
183
Running the model
12
0.0
1

TEXTBOX
10
20
160
38
Setup
12
0.0
1

TEXTBOX
10
270
185
296
Additional visualization options
12
0.0
1

TEXTBOX
10
380
160
398
Variables
12
0.0
1

MONITOR
805
230
905
275
Distinct cultures
length remove-duplicates [culture] of turtles
17
1
11

@#$#@#$#@
## WHAT IS IT?

This model simulates how people become similar through interaction. The idea is based on Robert Axelrod’s _Dissemination of Culture_ (1997). In his paper, Axelrod notes that one universal feature of culture is that it is "something people learn from each other" and makes two assumptions: 1) People are more likely to interact with similar people, and 2) people become more similar after interactions. He goes on to cite three principles upon which his study is based on: 1) Agent-based modeling, 2) no central authority, and 3) adaptive (as opposed to rational) agents.

## HOW IT WORKS

In this model, each agent has two properties: culture and similarity. Culture represents the distinctive characteristics of an agent, and similarity represents how similar its culture is to its linked neighbors. Culture is randomly assigned to each agent in the simulation, and similarity is determined by the amount of overlap in cultures between an agent and its neighbors. Users do not know the assigned cultures, but they can see how similar an agent is to its neighbors. In each tick, an agent potentially interacts with one of its linked neighbors. Interaction depends on the similarity between two agents; the more similar an agent is to its neighbor, the more likely they are to interact. If an agent does interact with its neighbor, then its own culture is modified to become more similar to its neighbor. If agents do not interact, then culture is unaffected.

## HOW TO USE IT

To start, select one of five setup versions. These versions differ in how the agents are connected to one another. The options are Lattice, Mean Field, Random, Scale Free, and Small World.

-Lattice: Creates cube-length^dimension agents and arranges and links them to represent a lattice.
-Mean Field: Creates N agents and connects every agent to every other agent.
-Random: Creates N agents. Each agent then randomly selects one other agent and makes a link with that agent. Though each agent may only select one target, it is possible for one agent to be the target of many other agents.
-Scale Free: Arranges N agents into preferential groups determined by the m0 and m variables.
-Small World: Creates N agents and arranges them in a circle. Each agent is linked with its adjacent agents.

When using the Lattice, Random, or Scale Free setup, the Layout button may be pushed to assist in visualization. Push Layout again to stop the agent rearrangement. The radial-central button may also be useful for visualization purposes.

Once the model is setup and you are ready to run the simulation, press the Go button. The simulation may be run simultaneously, on each tick every agent interacts with a neighbor, or not, on each tick one agent is randomly selected to interact with a neighbor. As the simulation runs, agents will change color from gray to various shades of blue. The darker the shade of blue, the more similar an agent is to its linked neighbors. The number of distinct cultures is tracked during this simulation. Press the Go button again to stop the simulation. Press the Recolor button to examine the distribution of culture. Each color represents a distinct culture. The resize button can help better see the color of the agents if they are too small.

## THINGS TO NOTICE

Notice the change in shades of blue as the simulation goes on; concurrently, notice how the number of distinct cultures changes. When pressing the Recolor button, notice the relation between same culture/color and linked agents.

## THINGS TO TRY

Adjust the five sliders under the variable section to play with larger or smaller network sizes. Adjusting the m and m0 sliders will also change the composition of the preferential groups used in the Scale Free setup.

## EXTENDING THE MODEL

Whether or not an agent interacts with its randomly selected neighbor depends on their level of similarity. The more similar two agents are, the more likely they are to interact, and thus adjust the interactor's culture. By changing the interaction rule, one may examine how culture changes when agents are more or less likely to interact with those they are dissimilar too. This may be examined by adjusting the go function under the UPDATE RULES section of the code.

Additional setup procedures may also be coded and tested under this Axelrod model.

Under the current modeling choice, only the interactor changes its culture, the interactee is not affected by interaction. One potential extension is to have only the interactee change its culture, or to have both agents adjust their culture after interaction.

It may be interesting to test how the simulation runs if there are agents who never adjust their culture mixed in with those who do. It may also be interesting to model situations where two agents have asymmetric likelihoods of culture-changing interactions between themselves, e.g. for fixed similarity, agent A is more likely to adjust its culture after interacting with agent B than agent B is after interacting with agent A.

## RELATED MODELS

Confident Voter
Heterogeneous Voter
Social Consensus
Ising
Potts
Turnout

## CREDITS AND REFERENCES

Axelrod, Robert. 1997. "The Dissemination of Culture: A Model with Local Convergence and Global Polarization." _Journal of Conflict Resolution_ 41 (2): 203-26.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
0
Rectangle -7500403 true true 151 225 180 285
Rectangle -7500403 true true 47 225 75 285
Rectangle -7500403 true true 15 75 210 225
Circle -7500403 true true 135 75 150
Circle -16777216 true false 165 76 116

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270

@#$#@#$#@
NetLogo 5.1.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180

@#$#@#$#@
1
@#$#@#$#@
