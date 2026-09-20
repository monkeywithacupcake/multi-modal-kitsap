# multi-modal-kitsap

This project is an active working project. I do not guarantee that anything here works.

## Goal
Personal project to build a multi-modal routing engine for Kitsap, relying on Kitsap Transit for transit, walking, and biking. I know that there are open transit and routing models. I am attempting to build a routing model/ algorithm from scratch to learn the mathematical mechanics of public transit data as well as prioritized decisions from users - like I am willing to bike or walk x far or under y conditions. I am hopeful that I will be able to use open street map data and weight roads differently for walking vs biking, as there are some roads, like Silverdale Way between Byron and 303, where I am perfectly happy to walk becaus ethere are sidewalks, but I definitely do not like biking. 

Timeline wise, I am not sure how long this will take, but I am hoping to finish before end of calendar year 2026. At least with some of this working. 

## Language/tooling
I plan to start with python because it seems like a pretty low bar for me to hop into consuming the transit and osm data.

## Over time learning
I am going to use this as a bit of a record for myself, and that is not normally how i use a readme, but I don't want to keep a separate journal right now. 

### Week 1

- get transit data: I was able to read in the static Kitsap Transit routes and stops. I had done this previously in R, and I have the live GTFS feed on my wall, but this is the first time that I pulled it via python. I ran into some hurdles, but nothing big.
- get osm data: I was able to read in the OSM data for the county. I also had this previously when I was working on contributing to OSM and flagging private roads as well as bike parking and unlabeled paths.

### Week 2
- identify nearest node: Match up the nearest OSM node to the bus stops. This was pretty straightforward, but I had to read over docs because I only previously knew how to do this with simple features (sf) in R. 
- made some sketchy graphs to help orient myself with the density of the challenge. Really, if points a and b are outside of the KT routes (generally east of 3), the user's preference between bike and walk will be the only issue, and then we are routing based on preferences. East of 3, during transit running times, we will have to consider different preference weights for each edge when considering getting to point b directly from point a as well as any buses that might be between the two. (i think ideally, we would also allow a bus that overshoots, but that is a problem for the future).
- read about Dijkstra's algorithm - which I was hoping would work here, but it might be a challenge when considering that bus routes are fixed and safety (or other preference weights) could impact whether user makes it to a certain bus. 

**next step:** make a simple Dijkstra over a few nodes. I'd like to have a more solidy grasp of this algorithm - actually making it work rather than reading and nodding along. 

