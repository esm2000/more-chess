# Chess Patch 1.1

## Introduction
A online revision of the classic game of Chess. The idea came from a [thread](https://www.reddit.com/r/leagueoflegends/comments/3yf3d3/chess_patch_11_notes_by_riot_games/) posted to Reddit that parodied the balance of a video game. However, the rules were so intriguing that I was interested in bringing it to life. 

## Quickstart

### Prerequisites 
Ensure you have the latest version of [node and npm](https://nodejs.org/en/). 

### Instructions

To run locally open your terminal and navigate to the root directory of the project and run

```
npm start
```

## Patch Notes
There are quite a few changes here that will dramatically alter gameplay, especially large buffs to Bishops and Queens as well as some nerf for Knights and Rooks.

### Chessman Updates

#### Pawns
To speed up games the behavior of pawns where altered. Pawns often determine the structure of a game.

* If your average piece value is at least 2 points higher than your opponent's, your pawns become more effective against enemy pawns. Their capture range extends to directly in front of them as opposed to diagonals, but only when capturing other pawns.
* If your average piece value is at least 3 points higher than your opponent's, your pawns become more effective defending against enemy pawns. They can no longer be captured by enemy pawns.

#### Knights
The ponies of the board were a bit strong, especially in the early game. This change brings them more in line with other units by removing their ability to ignore unit collision and will allow other pieces more counterplay against Knights.

* No longer can jump over other units

#### Bishops
As long range marksmen, bishops excel at dealing damage from long ranges, but are easily flanked and picked off by other units. This change will more clearly define these strengths at a distance and weaknesses in close combat.

* Bishops' movement and capture actions Energize them, building up to 100 stacks. Upon full stacks, the Bishop's next capture action can now capture other pieces by landing on any square adjacently diagonal to the opponent's piece.
* Bishops can now be captured by landing on any square adjacent to it, even those not on diagonals.
* Additionally, if a Bishop is threatening to capture a piece, at the end of the Bishop's turn the opposing piece gets a stack of a debuff. On the third hit of the debuff, the Bishop may immediately capture the enemy piece.

#### Rooks
Rooks have long abused their ability to control an entire file, or row of squares, and dominate the flow of the board. All pieces control over files are being toned down, but it was decided to nerf the powers of Rooks regardless just for good measure. The mid game power of Rooks was too high for a piece meant to shine late game. The changes below reflect both of these, and will separate the good Rooks from the great ones.

* Rooks movement and capture range now scales with game length. It begins at 3 and gains 1 maximum movement and capture range every 5 turns after the 10th turn of the game.

#### Queens
Queens have long been a strong piece and because of the dyanamic gameplay they offer they're being buffed. They are flashy and interesting to watch competitively and therefore deserve additional power to shine even brighter.

* If a Queen moves but does not capture an enemy piece, it instead stuns all enemy pieces adjacent to it for 1 turn.
* Additionally, Queens now reset on kills and assists. If a Queen captures a piece and is not in danger of being capture herself afterward, she gains the ability to move or capture again. Assists are defined as being able to capture a piece, but allowing another unit to last hit it instead.

#### Kings
We felt Kings were not making a big enough impact and we boring and uninteresting to play, so we are adding minigames to them.
* Every 10 turns, a Sword in the Stone appears on a random location on the map. The King can pick up the sword and prove he is the rightful ruler of the throne. Upon picking up the sword, he gets the Divine Right buff, allowing him to prevent 1 instance of check or checkmate.
* Additionally, Kings now benefit from his teammates killing enemy units. For every enemy unit that is captured that is not captured by the King, the King gets +1 gold. The King can use his gold to purchase additional units upon visiting his base (starting square), with an exchange rate of 2 gold per 1 point value of the piece being bought. However, Queens cannot be bought in this way.

### General Gameplay Updates

#### File Control
As mentioned previously with the Rook nerfs, pieces' abilities to monopolize control over a file are being toned down. Hopefully this will make for more interesting games.

* Pieces moving down a file cannot move past the center unless they are already on the center. The center is defined as the 4x4 square in the center of the board, enclosed between c3, c6, f3, and f6.

#### White Side Advantage
For millennia White side players have had the advantage in winrate over their Black side counterparts. To maintain game balance slight adjustments are being made to give Black players a better competitive chance. 

* Black players now start the game with a pawn on d6 instead of d7.

#### Neutral Objectives
As part of our attempt to quicken the pace of games, a few neutral objectives are being added to the board so that players are more inclined to break mid game gridlocks.

These objectives take the form of neutral pieces that can be captured. This occurs by bringing a piece's hitpoint to 0. Moving a unit adjacent or on top of the neutral piece removes 1 hitpoint. However, pieces that spend more than 1 turn adjacent or on top of a neutral piece are immediately destroyed.

If a neutral monster goes 3 turns without losing health, it is instantly healed to full health.

Buffs granted by capturing neutral pieces are given to the player who reduces its health to 0.

*Dragon: 5 hp*

Every 10 turns, the Dragon spawns on the h4 square. Capturing dragon grants a stacking buff.

- 1 stack - Pawns gain +1 movement 
- 2 stacks - All pieces deal +1 bonus damage to neutral pieces
- 3 stacks - Pieces ignore unit collision with ally pawns 
- 4 stacks - Pieces ignore unit collision with ally units 
- 5 stacks - Pieces can capture enemy units by occupying an adjacent square. Only 1 unit per turn can be captured still, and in cases where multiple units can be captured in this way, it is up to the opponent's choice which to lose. This buff lasts 3 turns.

*Board Herald: 5 hp*

Every 10 turns, spawns on the a5 square. Grants a buff only to the piece who captured it. Pawns adjacent to the piece can capture other pawns and pieces 1 square in front of them.

*Baron Nashor: 10 hp*

Spawns on the a5 square every 15 turns after the 20th turn. Grants a buff to all pawns. All ally pawns can capture other pawns and pieces 1 square in front of them. Additionally they cannot be captured by other pawns. If enemy pawns currently are immune to your pawns, Baron buff negates this for the duration of the buff.
