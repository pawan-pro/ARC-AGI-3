ARC3 Offline Agent Evaluation and Recording Viewer
Hi everyone, sharing a reproducible ARC3 notebook for offline agent evaluation and debugging.

Notebook: ARC3 Offline Agent Evaluation and Recording Viewer

What this notebook adds:

Runs the copied agent offline
Computes per-game action-count and score stats on public games
Visualizes recordings for behavior inspection and debugging
Key point: The pipeline runs through the official main.py command path, so behavior is closer to the real evaluation runtime than using a custom simulator from environment files

Run artifacts:

recordings
summary.csv
summary.txt
scorecard.json
run.log
Visualization snapshots: 






3
8 Comments
2 appreciation comments
Hotness
 
Comment here. Be patient, be friendly, and focus on ideas. We're all here to learn and improve!
This comment will be made public once posted.


Post Comment
Bridgeport
Posted 18 days ago

· 361st in this Competition

Thank you! Were you able to reproduce performance of published and officially evaluated agents?


Reply

React
Duc-Cuong Le
Topic Author
Posted 17 days ago

· 536th in this Competition

Thanks for the question. I was able to run the code from https://www.kaggle.com/code/itsyoursumit/forge-arc-agi-3-agent by simply replacing my agent write cell with theirs, so compatibility-wise it does run in this pipeline. The failure I hit was Kaggle storage, not import/runtime compatibility: that agent uses MAX_ACTIONS = infinity, so recording files become too large and eventually exceed storage quota. It should run to completion if MAX_ACTIONS is capped, or if rollout length is constrained to the competition 6-hour runtime budget. I am rerunning with those limits for fair comparison.


Reply

React
Greg Kamradt
Competition Host
Posted 17 days ago

· 583rd in this Competition

What max action limit resulted in a clean run? (not hitting the storage failure)


Reply

React
The Loose Goose
Posted 21 days ago

· 158th in this Competition

Thanks! That’s a great piece of work, really appreciate it.


Reply

1
Van-Phuc Huynh
Posted 14 days ago

· 20th in this Competition

Sorry if this question has already been asked, but I’d like to clarify what the maximum leaderboard score is.

Is the maximum score 1.0 , or can it reach 100?


Reply

React
The Loose Goose
Posted 14 days ago

· 158th in this Competition

Its decimal, so no one passed 1% as for now. Max 100.00.


Reply

React
Van-Phuc Huynh
Posted 14 days ago

· 20th in this Competition

Thanks, that’s a good sign—it shows we still have a lot to work on in the early stage of the competition.


Reply

React
Durga Kumari
Posted 18 days ago

That's great


Reply

React

Appreciation (2)
min
Posted 18 days ago

Thanks for sharing！

Greg Kamradt
Competition Host
Posted 21 days ago

· 583rd in this Competition

Thanks for sharing