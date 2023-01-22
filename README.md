# Stereo-Matching
Stereo matching

### 1. Cost Computation: 
Census cost = Local binary pattern -> Hamming distance
<img width="600" alt="截圖 2023-01-22 下午4 45 15" src="https://user-images.githubusercontent.com/96567794/213907494-18d38ff1-3b6d-49c3-855e-ada136363b67.png">

### 2. Cost Aggregation:
Refine the cost according to nearby costs. [Tips] Joint bilateral filter (for the cost of each disparty)
<img width="600" alt="截圖 2023-01-22 下午4 46 40" src="https://user-images.githubusercontent.com/96567794/213907543-a46d82e7-3d75-465f-b7f1-387f469541a6.png">

### 3. Disparity Optimization:
Determine disparity based on estimated cost. [Tips] Winner-take-all
<img width="600" alt="截圖 2023-01-22 下午4 47 23" src="https://user-images.githubusercontent.com/96567794/213907568-77e44566-d581-4c6a-b9a5-a15708bcc55a.png">

### 4. Disparity Refinement: 
Do whatever to enhance the disparity map.[Tips] Left-right consistency check -> Hole filling -> Weighted median filtering
<img width="600" alt="截圖 2023-01-22 下午4 47 48" src="https://user-images.githubusercontent.com/96567794/213907579-88aa24ef-e903-4f62-b138-e98b9b4c87e2.png">
<img width="600" alt="截圖 2023-01-22 下午4 48 00" src="https://user-images.githubusercontent.com/96567794/213907582-f5899bb1-060e-4785-bd06-c50633ab80bc.png">
<img width="600" alt="截圖 2023-01-22 下午4 48 12" src="https://user-images.githubusercontent.com/96567794/213907589-ad9a928d-df1a-4690-ac33-82b8b9f541ed.png">
