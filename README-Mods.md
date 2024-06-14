I created a web_plan action type 
which has the associated files api_outcome_determiner.py and web_plans_actions

If the api is reachable, we take teh first action from the outcome list, otherwise the second, this probably needs to be ironed out later. 

I created a slot_fill_more action type. Which is converted to dialouge type action. 

As of right now, in slot_fill_more action you can only have fflag values, and nothing else. 