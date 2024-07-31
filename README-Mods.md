I created a web_plan action type 

# Web Plan Action

This action is based on `web_action` action type. Essentially, this is a stripped down version of the web_action. The main purpose is for debugging. This should be replaced by fixing the issue that hierarchical planner cannot be called from inside `web_action` action type. 

During the initialization of the action, we dump all the state variables into `dump.json` file. This is the file used by the `upf_server` to create the mapping. This can be improved by adding at the end of the `execution_call_back` and sending the field values directly over the `request` instead of dumping the values into a file. 


# API Outcome determiner

This action is again based on `web_call_outcome_determiner.py`. The idea is the same. Depending on whether `web_plans_action` succeeded or not, the outcome is determined and the `"msg"` value is set. 
