# Interesting break point is on line 54 of plan.py

The thing that i  am not sure, is that , can we jump from one action to another. 

Because for me it looks like, 

the next step can only depend on the current and the outcomes that might result out of it. 

My working branch works now, because the outcome determiner always outputs that the first outcome has value of 1, regardless of the input.

--> One Idea that I had, was to see where the request is coming from and send it to different outcome determiners? for example to rasa or just something that sets value to one? 

Meaning, if the message is send from new-message endpoint, it will get treated differently than system-message? 

But probably, easier way would be to just, create a new-message endpoint and using custom context determiner, and rank the outcomes based on that. 


# In talk with Jean we agreed on 

1. That we will create a normal dialogue filling situation
2. Maybe a negating system too. But I think this runs the same problem as the one before. 