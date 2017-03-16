# Kinkara
Library to manage files (retention, deletion, moving, rule creation) based on multiple conditions.

While managing data on HDFS/S3 and even local file system, there's often a need for an easy file management tool to do things with multiple conditions like, for example, "move all files with size >= 2 GB AND that were created before May 2016 OR were created by 'root' AND contain(s) the lines "terminal command" inside them to a new directory.
Or, delete all files which contain the word "temp" inside them OR were last modified last month OR whose filenames are all just numbers! (Might be log files). 
Here's one tool I created to do all those sort of operations - Kinkara. 
