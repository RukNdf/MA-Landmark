(define (problem pb1)
  (:domain simple)
  (:objects
   a - t1
   b - t2
   )

  (:init
    (p a)
    (q b)
  )
  (:goal (and
    (p a)
    (q b)
  ))
)