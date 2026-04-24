Simplified submission framework
The official notebooks show how to submit your agents to run on ARC-AGI3, but they're pretty complicated. Also, they do nothing if you're not actually submitting - they don't actually run on the 25 training games then.

We've made this notebook that shows a more straightforward way to interact with the ARC-AGI3 environments. It will run on the 25 training games when not submitting (including diagonstics), and on the 110 test games when submitting.

Good luck!

https://www.kaggle.com/code/jeroencottaar/simplified-submission-approach/


9
3 Comments
1 appreciation comment
Hotness
 
Comment here. Be patient, be friendly, and focus on ideas. We're all here to learn and improve!
This comment will be made public once posted.


Post Comment
Gabriel Mirea
Posted 6 days ago

· 475th in this Competition

Hey, any idea why this scores 0.00 while the official random example scores 0.something? I tried increasing the max iterations to 100k and making it parallel w/ 20 threads, still 0.00. On the test set it scores something (solving some first levels, and even 2nd levels on 2 problems). I would expect it to score at least one level on the LB as well.


Reply

React
Gabriel Mirea
Posted a day ago

· 475th in this Competition

I figured it out, posting here for posterity. My first attempt at parallelising the code was calling env.make() in each process, you can't do that as it will open a scorecard for each process, and end up with a 0 code. I followed the code in the agent repo and called make() on the main thread, and then parallelised it, works like that - code scored 0.11 on LB.


Reply

React

Appreciation (1)
Greg Kamradt
Competition Host
Posted 24 days ago

· 583rd in this Competition

Thank you for this contribution