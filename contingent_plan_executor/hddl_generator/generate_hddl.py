

def generate_hddl(problem_name, domain_name, predicates_list, task_based_goal_dict=0): 
    
    
    formatted_objects = "engineFire - FireType"
    formatted_predicates = "\n".join(f"({predicate})" for predicate in predicates_list)
    formatted_goal = "(react_to_engine_fire_in_flight engineFire )"
    text = f""" (define (problem {problem_name})
    (:domain {domain_name})
    (:objects
        {formatted_objects}


    )

    (:htn
        :subtasks
        (and
                {formatted_goal}
                

        )

    )


    (:init
        {formatted_predicates}

    )
    )
    """
    return text 
