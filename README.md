# BetweenTwoCities

Between Two Cities is a tile-based board game where each pair of players must collaborate to construct a "city" of 4x4 grid of tiles. I was playing with friends when someone said, "I wonder what the maximum possible game score is"? I expected it to only take a handful of hours; in reality, working out all the algorithmic details took a while!

This project implements a calculator which determines the score for a given board arrangement, and a fairly unintelligent random search which aims to find the optimal solution. 

Each tile contains a different type of urban district: shopping, factories, entertainment, offices, parks and houses. Points are scored as follows:
- *Shopping districts* are scored in edge-to-edge runs in a column or row, with 2, 5, 10 or 16 points for a run of 1, 2, 3 or 4 tiles respectively. Each tile may only be scored once.
- *Factories* are simple: each one scores 4 points. In reality in the board game, each factory is only worth 4 points if you are the player with the largest number of factories; however, since the program aims to calculate the maximum possible score for a 4x4 board, the multiplier is fixed at 4.
- For *entertainment venues*, the key is variety. There are four kinds of venue: pub, restaurant, music or hotel (4). Points are earned depending on the number of different types of venue: 1, 4, 9 and 17 for 1, 2, 3, 4 different types of venue respectively.
- *Offices* score 1, 3, 6, 10, 15 or 21 points for increasing numbers of offices, but for each office placed next to an entertainment venue, there is a 1 point bonus.
- *Parks* can score highly, but must be contiguous to do so. A single park tile by itself is 2 points, but connect it edge-to-edge with others, and you score 8, 12, 13, or points for 2, 3, 4 or 5 parks.
- *Houses* have a value between 1 and 5 depending on how many other types of tile are in your city. However, place a house next to a factory, and that house is only worth 1 points.

In a standard edition of Between Two Cities, there are 24 shopping, factory and park tiles, and 28 entertainment (7 of each), office and house tiles.

Each board arrangement is implemented as an instance of the `Board` class, which contains methods which calculate the points earned for each type of tile. Some of these (e.g. factories) are trivial to implement, but some (parks and shopping districts) required a little more thought:
- Calculating parks required sorting each park in a "bin" corresponding to each contiguous park area, combining bins when a bridging park tile was added, and scoring each one separately.
- Shopping districts should be intuitive to score (and are easy for humans!), but in reality, the problem was quite complex. High-scoring boards are unlikely to have many shopping districts, but it soon becomes tricky when there are a number of intersecting runs of shopping tiles. This is due to the fact that each tile may only be scored once, and so the algorithm must choose which horizontal or vertical run to eliminate in which order. This creates a branching tree of solutions which must be navigated. My solution therefore involves a recursive function `evaluate_node()` which examines each node of the decision tree, examines the possible options, and selects the most highly scoring option. Memoization is used to store the score of each node in a dictionary to increase the speed of processing, and these cached board structures are simplified as far as possible in order to eliminate duplicates (rotations of the board are factored in too, but not reflections).

The program searches approximately 10,000 solutions per second, and the most highly-scoring boards are saved to disk in JSON format so that processing can be paused and then resumed from where it was left off. Currently, the optimal solution found is 68 points (there are at least four of them). There are some interesting trends in terms of strategy:
- All have 17 points for entertainment, with only one of each type of venue
- 1 factory seems to be optimal (obviously none adjacent to a house), and 0 shopping districts. Clearly the cost of not getting the full x5 multiplier on a house is worth the extra tile (which would otherwise only score an additional 2 points for shopping). For all the effort spent creating the recursive memoization algorithm, it doesn't seem to be a good strategy for the game.
- Parks come in groups of 2, usually only one group (or two). 8 points is much more than 2, and not that much less than 12.
- Offices are the real high-scorer. All the top solutions have 27 points (6 offices, each with a +1 bonus for being next to an entertainment venue). This seems to be the best strategy in terms of maximising points.

There is a bug/feature where sometimes, it is more beneficial to score two runs of 3 shopping districts rather than one run of 4 ("." denotes any non-shopping tile):

Example A
                        
. s s s       
. . s .       
. . s .       
. s s s

One run of 4 (16 points) + four runs of 1 (2x2=8 points) = 24 points  (the algorithm chooses this) \
OR \
Two runs of 3 (2x10=20 points) + one run of 2 (5 points) = 25 points  (this scores higher) \

Example B
                        
s s s .       
. s s s       
. s . .       
s s s .

One run of 4 (16 points) + one run of 2 (5 points) + four runs of 1 (2x2=8 points) = 29 points  (the algorithm chooses this) \
OR \
Three runs of 3 (3x10=30 points) + one run of 1 (1 point)                          = 31 points  (this scores higher) \

Since it is not clear in the rules of the game which option is preferred in this case (it is a very poor strategy for a high number of points), I have decided to go for the computationally easier option (the lower score) of always eliminating the highest order runs wherever possible, as this usually gives the highest score (especially in the boards which are likely to be record-scoring).

Future optimisations may be made to the board generation code to make it more sensible, as you're unlikely to have a high-scoring city with more than (or less than!) one of each kind of entertainment venue, or more than 3 parks in a board, for example). If such optimisations are made, a more exhaustive (rather than random) search may be more possible.

I found the problem-solving for the shopping district algorithm particularly enjoyable. It wasn't immediately obvious what the best algorithm would be, and I tried a few overcomplicated recursive options before settling on this one. Using a class for the board structure should have been an obvious starting point too, and next time I come across a similar problem, I'll do that instead!
