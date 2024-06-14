from hovor.outcome_determiners.outcome_determiner_base import OutcomeDeterminerBase

class ApiOutcomeDeterminer(OutcomeDeterminerBase): 
    
    
    def rank_groups(self, outcome_groups, determination_progress):
        progress = determination_progress.create_child()
        status = determination_progress.action_result.get_field("suceeded")
        
        ranked_groups = [(outcome_groups[0], 1), (outcome_groups[1], 0)]
        ranked_group_reversed = [(outcome_groups[1], 1), (outcome_groups[0], 0)]
        
        if status: 
            return ranked_groups, progress
        else: 
            return ranked_group_reversed, progress
        


            
        
        