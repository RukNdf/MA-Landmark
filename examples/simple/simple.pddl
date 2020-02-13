; This is a comment line
(define (domain simple) ; There is no block comment like
  (:requirements :strips :typing)

  (:types
  t1
  t2
  )

  (:predicates
    (p ?v1 - t1)
    (q ?v1 - t2)
  )
  (:action ac1
    :parameters (?p1 - t1 ?p2 - t2)
    :precondition (and
      (p ?p1)
    )
    :effect (and
      (q ?p2)
    )
  )
)