# Stereo-Matching
Stereo matching

### 1. Cost Computation: 
Census cost = Local binary pattern -> Hamming distance
### 2. Cost Aggregation:
Refine the cost according to nearby costs. [Tips] Joint bilateral filter (for the cost of each disparty)
### 3. Disparity Optimization:
Determine disparity based on estimated cost. [Tips] Winner-take-all
### 4. Disparity Refinement: 
Do whatever to enhance the disparity map.[Tips] Left-right consistency check -> Hole filling -> Weighted median filtering
