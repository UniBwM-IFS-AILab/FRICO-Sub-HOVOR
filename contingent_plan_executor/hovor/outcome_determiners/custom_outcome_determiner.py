from hovor.outcome_determiners.outcome_determiner_base import OutcomeDeterminerBase
import random

class CustomeOutcomeDeterminer(OutcomeDeterminerBase): 
    # Ignore this, use api_outcome_determiner
    
    def rank_groups(self, outcome_groups, progress): 
        
        ranked_groups = []
        
        for group in outcome_groups: 
            outcome_description = progress.get_description(group.name)
            
            # conditions  = outcome_description["Context"]
            
            # evaluated_condition = True 
            
            # for context_var, context_var_config in conditions.item(): 
                
            #     print(context_var, context_var_config)
            rank = random.choice([0,0])
            ranked_groups.append((group,rank))
        ranked_groups[0] = (ranked_groups[0][0],1)
        return ranked_groups, progress