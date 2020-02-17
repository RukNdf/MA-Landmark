(define (domain ma-blocksworld)
  (:requirements :strips :negative-preconditions)
  (:predicates (clear ?x) (onTable ?x) (holding ?x) (on ?x ?y) (equal ?x ?y) (agent ?ag) )

  (:action pickup
    :parameters (?ag ?ob)
    :precondition (and (clear ?ob) (onTable ?ob) (agent ?ag) )
    :effect (and (holding ?ob) (not (clear ?ob)) (not (onTable ?ob)))
  )

  (:action putdown
    :parameters (?ag ?ob)
    :precondition (and (holding ?ob) (agent ?ag) )
    :effect (and (clear ?ob) (onTable ?ob) (not (holding ?ob)))
  )

  (:action stack
    :parameters (?ag ?ob ?underob)
    :precondition (and (clear ?underob) (holding ?ob) (not (equal ?ob ?underob)) (agent ?ag) )
    :effect (and (clear ?ob) (on ?ob ?underob) (not (clear ?underob)) (not (holding ?ob)))
  )

  (:action unstack
    :parameters (?ag ?ob ?underob)
    :precondition (and (on ?ob ?underob) (clear ?ob) (not (equal ?ob ?underob)) (agent ?ag) )
    :effect (and (holding ?ob) (clear ?underob) (not (on ?ob ?underob)) (not (clear ?ob)))
  )
)