(define
    (domain frico_fire)
    (:requirements :strips)
    (:types )
    (:constants )
    (:predicates
        (know__request_emergency_help)
        (maybe-know__request_emergency_help)
        (request_emergency_help)
        (know__fire_type)
        (maybe-know__fire_type)
        (know__request_engine_fire_help)
        (request_engine_fire_help)
        (know__request_electric_fire_help)
        (request_electric_fire_help)
        (informed)
        (know__instrument_fire_enum)
        (maybe-know__instrument_fire_enum)
        (know__electrical_fire)
        (electrical_fire)
        (know__fire_color)
        (know__goal)
        (goal)
        (force-statement)
    )
    (:action get-initial_help_request
        :parameters()
        :precondition
            (and
                (not (know__request_emergency_help))
                (not (maybe-know__request_emergency_help))
                (not (force-statement))
                (not (request_emergency_help))
            )
        :effect
            (labeled-oneof get-initial_help_request__set-emergency_help_type
                (outcome update-generic_fire_emergency
                    (and
                        (maybe-know__request_emergency_help)
                        (request_emergency_help)
                        (force-statement)
                    )
                )
                (outcome update-engine_fire_emergency
                    (and
                        (request_engine_fire_help)
                        (know__request_engine_fire_help)
                        (informed)
                        (know__request_emergency_help)
                        (force-statement)
                    )
                )
                (outcome update-electric_fire_emergency
                    (and
                        (know__request_electric_fire_help)
                        (request_electric_fire_help)
                        (informed)
                        (know__request_emergency_help)
                        (force-statement)
                    )
                )
                (outcome update-no_its_good
                    (and
                        (informed)
                        (know__request_emergency_help)
                        (force-statement)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action get-fire_information
        :parameters()
        :precondition
            (and
                (request_emergency_help)
                (not (know__fire_type))
                (not (maybe-know__fire_type))
                (not (know__request_emergency_help))
                (not (force-statement))
                (maybe-know__request_emergency_help)
            )
        :effect
            (labeled-oneof get-fire_information__set-emergency_type
                (outcome update-engine_fire
                    (and
                        (know__fire_type)
                        (not (maybe-know__request_emergency_help))
                        (know__request_emergency_help)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action get-fire_color_information
        :parameters()
        :precondition
            (and
                (request_emergency_help)
                (know__fire_type)
                (not (maybe-know__fire_type))
                (not (maybe-know__request_emergency_help))
                (know__request_emergency_help)
                (not (force-statement))
            )
        :effect
            (labeled-oneof get-fire_color_information__set-fire_color
                (outcome update-fire_color
                    (and
                        (informed)
                        (know__fire_color)
                        (force-statement)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action complete
        :parameters()
        :precondition
            (and
                (informed)
                (not (force-statement))
            )
        :effect
            (labeled-oneof complete__finish
                (outcome finish
                    (and
                        (goal)
                    )
                )
            )
    )
    (:action dialogue_statement
        :parameters()
        :precondition
            (and
                (force-statement)
            )
        :effect
            (labeled-oneof dialogue_statement__reset
                (outcome lock
                    (and
                        (not (force-statement))
                    )
                )
            )
    )
)