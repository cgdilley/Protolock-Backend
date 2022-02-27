# Protolock Backend

This repo contains the backend code for solving Mezzonic Protolock puzzles
from Zereth Mortis, and is generalized to be able to support additional similar puzzle
types if I ever feel like implementing them.

The webpage for checking this out is at:  [protolock.sprelf.com]()
The repo for the webpage's code is found [here](https://github.com/cgdilley/Protolock-Web).

## Usage

All code inside the `src` directory is uploaded to a Lambda function on AWS using the Publish.py script.

This Lambda is invoked by an endpoint in an AWS API Gateway via `api.protolock.sprelf.com/solve [POST]`.

## The puzzles

Right now, only Mezzonic Protolock puzzles are implemented.

### Mezzonic

This puzzle consists of a 5x5 grid of squares that can either be in an ON or an OFF state.
A user interacts with this puzzle by clicking individual squares in the grid.  Doing so
flips the state of the clicked node; that is, turns it OFF if it's ON, and vice versa.
It also does this for all 4 adjacent squares in a `+` shape.  This does not wrap around the
board; if a square at the edge of the board is clicked, fewer squares will be flipped.

The puzzle begins by having a random selection of squares turned ON and OFF.  The goal
is to click the correct squares so that all squares are eventually in the OFF state.

#### Observations

1. Order of moves doesn't matter.  At the end of the day, the goal really is to ensure
that any ON squares are activated an odd number of times in total, and the OFF squares an
even number of times, and ordering does not affect this.
2. Making the same move twice is the same as not making the move at all, regardless of
any other moves before, after, or between.
3. Some states are unsolvable.  This likely means the puzzle is set up by performing the
puzzle in reverse:  starting with an empty board and choosing to activate some number of
squares at random in the same way a user might.  It's the user's goal to identify those
exact squares, and there will be no other solutions.


#### Path-finding solution

One approach is to treat this the same as a path-finding problem, and apply an appropriate algorithm
for such a problem.

Usually, a path-finding problem consists of having a series of connected nodes, and trying to find
the shortest path across the available edges connecting those nodes to get from a designated starting
node to an ending node.  To generalize this further, we can think of this in terms of states, which have
transitions to a certain defined collection of adjacent states.  Each of these transitions has a
particular cost, and we may be able to approximate the proximity of a given node to the end node, and
this is all intuitive when thinking in terms of physical space.

I wanted to think of this problem similarly:

 - Each 'node' is a particular board state; the specific squares that are turned OFF or ON
 - Each 'edge' (or 'transition') is a single click on a square that flips squares to OFF or ON,
generating a new state
 - The starting node is the initial given board position, and the ending node is the board with
all squares toggled OFF
 - Each transition is equal in value (just one move)
 - Proximity to the goal can be estimated simply by the number of squares left that are ON

I did some standard A*-like approaches (see BasicAlgorithm and LookaheadAlgorithm), but also
a modification that accounted for the orderless property of this puzzle (see OrderlessAlgorithm 
and OrderlessLookaheadAlgorithm).

#### Tree-search solution

Instead of thinking of individual board states, this solution just thinks about all the possible
combination of moves, and tries to find the one that gives the correct result.  The number of
possible combinations of moves are:

```
  __ 25                  
 \          (25 choose i)
 /__ i = 1  
```

which is a lot.  However, for each combination, we can estimate how close it would bring the board
to the final solution by counting the number of squares still ON, and explore options that have
a lower score first.

The process of navigating through these combinations can be thought of as like a tree traversal.
The root node is an empty set of moves, and the children of that root node are sets containing
exactly one square coordinate, for (0, 0) to (4, 4).  Then, we can start exploring further down
the tree from any of these children by generating their own children, except with the restriction
that no two nodes anywhere in the tree may contain the same set of coordinates.  This means
if the node `{(0, 0)}` has a child `{(0, 0), (0, 1)}`, then `{(0, 1)}` cannot have `{(0, 1), (0, 0)}` as 
a child.

Any time we want to iterate through the children of a particular node, we find all available moves we can 
add to the node's set of moves that hasn't been found elsewhere in the tree, and we then
iterate through these in order by how close they are perceived to be to the end goal.

With this arrangement, we can do several traditional modes of traversal (breadth-first or depth-first),
or some combination of the two that leverages this evaluation of the quality of the node.

## The code

Everything related to algorithms and pathfinding can be found in the `PathFinding` module.

Everything related to a particular game modes can be found in the `Games` module.

All other modules have basic utilities and helper classes.

The code is run by calling the `main()` function in the `Main.py` script, passing in arguments
as they would be expected to be structured by an API Gateway invoking a Lambda function (see 
code at bottom of that file for an example.)


