Skip to
content
Kaggle

Create
Search

Home

Competitions

Datasets

Models

Benchmarks

Game Arena

Code

Discussions

Learn

More

Your Work


Viewed

ARC Prize 2026 - ARC-AGI-3


NVIDIA Nemotron Model Reasoning Challenge


How to Get Started + Nemotron Model Reasoning Challenge Resources


Nemotron-3-Nano-30B-A3B-BF16


Rescore After Metric Update


Edited

Bookmarks

Measuring Progress Toward AGI - Cognitive Abilities


V3-ML-Predictive-Model


Stanford RNA 3D Folding Part 2


View Active Events

Skip to
content
Kaggle
Code Competitions - Errors & Debugging Tips
Goose with a question
You’re getting an error in a code competition. Now what? Writing code that works perfectly on unseen data is difficult, even for experts. Don't get discouraged or feel that you're the only one stuck.

To prevent probing, Kaggle does not provide highly specific debugging messages in code competitions (whereby Kaggle reruns your code on a hidden dataset). Submissions that error also count towards your team’s daily submission limit, otherwise such submissions could be used to mine for hidden information. However, we do provide a general class of error to point you in the right direction.

All reruns follow the same basic pipeline. First, we privately execute your notebook end-to-end with the competition dataset replaced by a hidden version with different data. Second, we validate that execution against the competition's constraints and extract your submission file from its output directory. Finally, we score that submission file. Each of these steps could run into errors.

Below are the classes of errors that your notebook might receive. Remember, just because two notebooks share the same class of error does not imply they share the same root cause!

Notebook Timeout: Your submission notebook exceeded the allowed runtime. Review the competition's Code Requirements page for the time limits. Note that the hidden dataset can be larger/smaller/different than the public dataset.
Notebook Threw Exception: While rerunning your code, your notebook hit an unhandled error. Note that the hidden dataset can be larger/smaller/different than the public dataset.
Notebook Exceeded Allowed Compute: This indicates you have violated a code requirement constraint during the rerun. This includes limitations in the execution environment, for example requesting more RAM or disk than available, or competition constraints, such as input data source type or size limits.
Notebook Inference Server Error: In some competitions, your notebook is required to run an inference server that Kaggle code will call in order to obtain batches of predictions. This error indicates an issue communicating with your server. Possible issues include not registering a required endpoint, the notebook crashing, or a request timing out, among other possibities.
Notebook Inference Server Never Started: The evaluation API's gateway was able to connect with the container hosting your code, but could not connect to the inference server within the time limit. This is most often caused by attempts to directly generate a submission file rather than running the evaluation API.
Submission CSV Not Found: Your notebook did not output the expected submission file (often submission.csv). The rerun of your notebook appears to have completed, but when we looked for your submission file, it wasn't there. This means it's possible to have bugs/errors upstream that halted execution and prevented the file from being written. Attempting to read a non-existent directory/file from a dataset is a common reason execution is halted (causing either Submission CSV Not Found or Notebook Threw Exception).
Submission Scoring / Format Error: Your notebook generated a submission file with incorrect format. Some examples causing this are: wrong number of rows or columns, empty values, an incorrect data type for a value, or invalid submission values from what is expected.
Kaggle Error: A rare system error. Please try resubmitting to resolve the error and contact Kaggle Support if it persists.
If you are stuck, we encourage you to apply the same types of debugging steps you might undertake when you have a full stack trace. Here are some tips to prevent errors and get you unstuck:

Take a deep breath, step away from the code, sleep or go for a walk, take your mind off it, then come back and examine with fresh eyes.
Use a submission to verify basic fundamentals are working. E.g. test if a pretrained model is present by trying to load it and submit the sample submission if it succeeds and erroring if it fails. You can also devise ways to communicate with yourself via the score or timing of your submission (e.g. intentionally submitting a very bad submission or sleep()ing a set amount of time).
You can use function decorators (see here for an example) to make your code extra robust. Work towards something that fails gracefully and still produces a score, then keep analyzing scores to determine just how often you think the code might be failing gracefully.
Build sanity checks into your pipeline - is the submission you produce the same number of lines as the sample submission? Is everything that should be positive actually positive? etc.
Anytime you are reading a file, consider the case where it may not exist.
Sometimes it is easiest to start with the sample submission, as opposed to trying to create a submission directly from the test set. It can be easy to lose an Id amidst the loops, joins, grouping, and data processing.
If all else fails, tear your pipeline down and rebuild it in a way that starts with a valid submission--such as submitting the sample submission, adds components one at a time, and verifies the output is still scoring. It's very common that the error is trivial or early in the code, and once you correct it the entire pipeline is back to being functional.
Keep at it and good luck!

